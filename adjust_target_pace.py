import streamlit as st
from google import genai
from google.genai import types

from helper import get_todays_date, adjust_target_pace_from_weather_at_location, SYSTEM_PROMPT_TARGET, WELCOME_MESSAGE_TARGET_PACE


st.title("Running Paces Calculator")
st.caption(WELCOME_MESSAGE_TARGET_PACE)

###set up gemini chat###
if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = "gemini-2.5-flash"
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
chat = client.chats.create(model=st.session_state["gemini_model"])
config = types.GenerateContentConfig(
    tools=[adjust_target_pace_from_weather_at_location,get_todays_date],
    system_instruction=SYSTEM_PROMPT_TARGET
)

if "messages_target" not in st.session_state:
    st.session_state["messages_target"] = []

chat_history = ""

# Display chat messages from history on app rerun
for message in st.session_state["messages_target"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    chat_history = chat_history + message["role"] + ": " + message["content"] + "\n"
    #print(chat_history)




if prompt := st.chat_input("Chat Here!"):
    st.session_state["messages_target"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    current_content = chat_history + "User: " + prompt
    #print(current_content)

    with st.chat_message("assistant"):
        st.markdown("*Thinking, please wait a moment...*")
    st.session_state["messages_target"].append({"role": "assistant", "content": "*Thinking, please wait a moment...*"})

    with st.chat_message("assistant"):
        response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=current_content,
                        config = config
                    )
        st.markdown(response.text)
    
    st.session_state["messages_target"].append({"role": "assistant", "content": response.text})
