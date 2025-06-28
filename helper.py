import os

import urllib.request
import sys
import json

import re
from dotenv import load_dotenv
import time
from datetime import date


def get_todays_date():
    """
    Provides today's date

    Returns:
        provides today's date
    
    """

    return str(date.today())

def get_weather_at_location(location: str):
    api_location = re.sub(r'[^a-zA-Z0-9\s]', '', location).replace(" ", "%20")
    #print(api_location)
    load_dotenv(override=True)
    weather_key = os.environ['WEATHER_KEY']
    #print(weather_key)
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/" + api_location + "?unitGroup=us&include=hours&key=" + weather_key + "&contentType=json"
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

def parse_forecast_for_dewtemp(days_from_today: int, hour_of_day: int, forecast: dict):
    dew = forecast['days'][days_from_today]['hours'][hour_of_day]['dew']
    temp = forecast['days'][days_from_today]['hours'][hour_of_day]['temp']
    return temp, dew

def adjust_pace(minutes: int, seconds: int, dewtemp: float):
    total_seconds = 60*minutes + seconds
    dewtemp_total = dewtemp[0] + dewtemp[1]
    #print(dewtemp_total)
    if dewtemp_total <= 100:
        return "No Adjustment"
    elif dewtemp_total >180:
        return "Not safe to run fast"

    adjustment = determine_adjustment(dewtemp_total)
    #print(adjustment)
    adjusted_seconds = adjustment*total_seconds+total_seconds
    result = time.strftime("%M:%S", time.gmtime(adjusted_seconds))

    return result

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

def adjust_pace_from_weather_at_location(location: str, days_from_now: int, hour_of_day: int, pace_minutes: int, pace_seconds: int):
    """
    Adjusts a given running pace based on the weather at the location on a certain date
    
    Args:
        location: the location that the runner will be running
        days_from_now: how many days from now the runner will be running, for today, this should be 0
        hour_of_day: the hour of the day the runner will be running
        pace_minutes: the minute portion of the pace, ex: for 5:16 pace, this would be 5
        pace_seconds: the seconds portion of the pace, ex: for 5:16 pace, this would be 16

    Returns:
        the adjusted pace that the runner should target
    
    """

    forecast = get_weather_at_location(location)

    dewtemp = parse_forecast_for_dewtemp(days_from_now,hour_of_day,forecast)

    result = adjust_pace(pace_minutes, pace_seconds, dewtemp)

    return result


WELCOME_MESSAGE = """Hi!
I'm here to help you convert your running paces when the weather is hot and humid!!

Please type below:

-what day and time you'll be running

-what city/town you'll be running in

-your target pace

And I'll do my best to give you an equivalent pace!
"""


SYSTEM_PROMPT = """
You are a helpful assistant and your job is to convert a user's target pace to a more appropriate pace given the weather.

The user should provide the location, date, time and pace.

You should then convert the user input to the arguments for the adjust_pace_from_weather_at_location function and call that function.

The adjust_pace_from_weather_at_location function will take the location, look up the temperature and dew point at the given date, time and location and then make the necessary adjustment

If you are unable to convert the user input to the arguments for the adjust_pace_from_weather_at_location function you should ask the user for additional information.

Once function calls are complete, you should tell the user the new pace they should target, the percent adjustment that was applied and 
very briefly explain that it was because of the temperature and dew point at the given time, date and location

If you need to know today's date, you can use the get_todays_date function.

You should assume the year is 2025."""

