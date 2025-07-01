import streamlit as st
import os

import urllib.request
import sys
import json

import re
from dotenv import load_dotenv
import time
from datetime import date

WELCOME_MESSAGE_LANDING_PAGE = """Hi!
I am a helpful assistent here to calculate running pace adjustments for you when the weather is hot and humid!!

Please use the navigation bar to the left to choose which task you would like me to complete:

##### **Target Pace Adjustment**

You give me the date, time and location you are planning on running, along with the pace you want to target and I will give you an equivalent pace to target based on the weather


##### **Performance Adjustment** 
 
You give me the date, time and location you ran, along with the pace you ran or performance (time and distance you ran) and I will give you an equivalent pace or performance based on the weather
"""

WELCOME_MESSAGE_PERFORMANCE_PACE = """Hi! Let me help you out with an equivalent pace from one of your performances!!

Please tell me in the chat box below:

-what day and time you ran

-what city/town you ran in

-the pace you ran or your performance (time and distance of the run)

And I'll do my best to give you an equivalent pace!
"""

WELCOME_MESSAGE_TARGET_PACE = """Hi! Let me help you out with an equivalent pace to target!!

Please tell me in the chat box below:

-what day and time you'll be running

-what city/town you'll be running in

-your target pace

And I'll do my best to give you an equivalent pace!
"""

###GENERAL FUNCTIONS###
def get_todays_date():
    """
    Provides today's date

    Returns:
        provides today's date
    
    """

    return str(date.today())

def determine_adjustment(total):
  
    conversion_dict = {
        100: 0.0,
        110: 0.005,
        120: 0.01,
        130: 0.02,
        140: 0.03,
        150: 0.045,
        160: 0.06,
        170: 0.08,
        180: 0.1,
    }
    for key in conversion_dict.keys():
        if total > key and total <= key+10:
            lower = key
            upper = key+10
            lower_adjust = conversion_dict[key]
            upper_adjust = conversion_dict[key+10]
    range1_ratio = (total-lower)/(upper-lower)
    range2_equivalent = (upper_adjust-lower_adjust)*range1_ratio+lower_adjust
    return range2_equivalent

def get_weather_at_location(location: str, date: str):
    api_location = re.sub(r'[^a-zA-Z0-9\s]', '', location).replace(" ", "%20")
    #print(api_location)
    load_dotenv(override=True)
    weather_key = st.secrets["WEATHER_KEY"]
    #print(weather_key)
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/" + api_location + "/" + date + "?unitGroup=us&include=hours&key=" + weather_key + "&contentType=json"
    #print(url)
    

    try: 
        ResultBytes = urllib.request.urlopen(url)
        # Parse the results as JSON
        jsonData = json.load(ResultBytes)
        
    except urllib.error.HTTPError  as e:
        ErrorInfo= e.read().decode() 
        print('Error code: ', e.code, ErrorInfo)
        sys.exit()
    except  urllib.error.URLError as e:
        ErrorInfo= e.read().decode() 
        print('Error code: ', e.code,ErrorInfo)
        sys.exit()
    return jsonData

def parse_weather_for_dewtemp(hour_of_day: int, forecast: dict):
    dew = forecast['days'][0]['hours'][hour_of_day]['dew']
    temp = forecast['days'][0]['hours'][hour_of_day]['temp']
    return temp, dew

###TARGET PACE ADJUSTOR###

def adjust_target_pace(minutes: int, seconds: int, temp: float, dew: float):
    
    
    total_seconds = 60*minutes + seconds
    dewtemp = temp + dew


    #print(dewtemp_total)
    if dewtemp <= 100:
        return time.strftime("%M:%S", time.gmtime(total_seconds)), 0
    elif dewtemp >180:
        return "Not safe to run fast", "N/A"

    adjustment = determine_adjustment(dewtemp)
    #print(adjustment)
    adjusted_seconds = total_seconds*(adjustment+1)
    result = time.strftime("%M:%S", time.gmtime(adjusted_seconds))

    return result, adjustment

def adjust_target_pace_from_weather_at_location(location: str, date: str, hour_of_day: int, pace_minutes: int, pace_seconds: int):
    """
    Adjusts a given target running pace based on the weather at the location on a certain date
    
    Args:
        location: the location that the runner will be running
        date: the date that the runner will be targeting the pace, in the format: YYYY-MM-DD
        hour_of_day: the hour of the day the runner will be running
        pace_minutes: the minute portion of the pace, ex: for 5:16 pace, this would be 5
        pace_seconds: the seconds portion of the pace, ex: for 5:16 pace, this would be 16

    Returns:
        the adjusted pace that the runner should target or "not safe to run fast" if the temperature + dew point is over 180
        the adjustment % used or "N/A" if the temperature + dew point is over 180
        the temperature for the date and time
        the dew point for the date and time
        
    
    """

    forecast = get_weather_at_location(location, date)

    temp, dew = parse_weather_for_dewtemp(hour_of_day,forecast)

    #get new pace and the adjustment %
    result, adjustment = adjust_target_pace(pace_minutes, pace_seconds, temp, dew)

    return result, adjustment, temp, dew

SYSTEM_PROMPT_TARGET = """
You are a helpful assistant and your job is to convert a user's target running pace to a more appropriate running pace given the weather at a given location.

The user should provide the location, date, time and pace.

You should then convert the user input to the arguments for the adjust_pace_from_weather_at_location function and call that function.

The adjust_pace_from_weather_at_location function will take the location, look up the temperature and dew point at the given date, time and location and 
then make the necessary adjustment and return the required details.

If the temperature + dew point is less than 100, then there will not be any adjustment made, and the adjustment % returned will be 0

If you are unable to convert the user input to the arguments for the adjust_pace_from_weather_at_location function you should ask the user for additional information.

Once function calls are complete, you should tell the user the new pace they should target, the percent adjustment that was applied and 
very briefly explain that it was because of the temperature and dew point at the given time, date and location

If you need to know today's date, you can use the get_todays_date function.

You should assume the year is 2025."""



###PERFORMANCE PACE ADJUSTOR###

def adjust_performance_pace(minutes: int, seconds: int, temp: float, dew: float):
    
    
    total_seconds = 60*minutes + seconds
    dewtemp = temp + dew


    #print(dewtemp_total)
    if dewtemp <= 100:
        return time.strftime("%M:%S", time.gmtime(total_seconds)), 0

    adjustment = determine_adjustment(dewtemp)
    #print(adjustment)
    adjusted_seconds = total_seconds/(adjustment+1)
    result = time.strftime("%M:%S", time.gmtime(adjusted_seconds))

    return result, adjustment

def adjust_performance_pace_from_weather_at_location(location: str, date: str, hour_of_day: int, pace_minutes: int, pace_seconds: int):
    """
    Adjusts a given performance running pace based on the weather at the location on a certain date
    
    Args:
        location: the location that the runner will be running
        date: the date that the runner achieved the performance pace, in the format: YYYY-MM-DD
        hour_of_day: the hour of the day the runner will be running
        pace_minutes: the minute portion of the pace, ex: for 5:16 pace, this would be 5
        pace_seconds: the seconds portion of the pace, ex: for 5:16 pace, this would be 16

    Returns:
        the adjusted pace for the performance the runner achieved
        the adjustment % used or "N/A" if the temperature + dew point is over 180
        the temperature for the date and time
        the dew point for the date and time
    """

    forecast = get_weather_at_location(location, date)

    temp, dew = parse_weather_for_dewtemp(hour_of_day,forecast)

    #get new pace and the adjustment %
    result, adjustment = adjust_performance_pace(pace_minutes, pace_seconds, temp, dew)

    return result, adjustment, temp, dew

SYSTEM_PROMPT_PERFORMANCE = """
You are a helpful assistant and your job is to convert a running performance from a user into an equivalent pace given the weather at a given location.

The user should will provide:
-location
-date
-time
-pace OR time and distance ran (ie: 5k in 20:00)

If the user has provided a time and distance ran, you should convert that into the pace they ran.
Ex: if the user ran a 5k in 20:00, the pace per mile would be 6:26.

You should then convert the user input to the arguments for the adjust_performance_pace_from_weather_at_location function and call that function.

The adjust_performance_pace_from_weather_at_location function will look up the temperature and dew point for the given date, time and location and 
then make the necessary adjustment to the pace provided and return the required details.

If the temperature + dew point is less than 100, then there will not be any adjustment made, and the adjustment % returned will be 0

If you are unable to convert the user input to the arguments for the adjust_pace_from_weather_at_location function you should ask the user for additional information.

Once the function calls are completed, if the user originally provided a time and distance, you should convert the adjusted pace back to the performance for that distance.
Ex: if the user ran a 5k and the adjusted pace was 7:00, then the 5k performance would be 21:45

Once you have all the information needed to complete the user's request, you should tell the user their adjusted pace (and adjusted performance if you calculated it), the percent adjustment
 that was applied and very briefly explain that it was because of the temperature and dew point at the given time, date and location

If you need to know today's date, you can use the get_todays_date function.
"""
