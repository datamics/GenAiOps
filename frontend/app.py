import streamlit as st
import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# API Configuration
load_dotenv()
API_URL = os.getenv("backend_host")


def init_session_state():
    """Initialize the session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your intelligent assistant. How can I help you today? I can access your internal documents of check the weather."
            }
        ]


async def process_response(prompt):
    try:
        print(f"Sending request with prompt: {prompt}")  # Debug output
        print(f"Chat history: {st.session_state.messages}")  # Debug output

        async with aiohttp.ClientSession() as session:
            chat_history = [
                {
                    "role": msg["role"],
                    "content": msg["content"]
                } for msg in st.session_state.messages
            ]

            request_data = {
                "message": prompt,
                "chat_history": chat_history
            }
            print(f"Request data: {request_data}")  # Debug output

            async with session.post(
                    f"{API_URL}/chat",
                    json=request_data
            ) as response:
                print(f"Response Status: {response.status}")  # Debug output
                if response.status == 200:
                    data = await response.json()
                    print(f"Response Data: {data}")  # Debug output
                    if isinstance(data, dict) and "response" in data:
                        return data["response"]
                    return "Sorry, invalid response format from server."
                else:
                    error_text = await response.text()
                    print(f"Error Text: {error_text}")  # Debug output
                    st.error(f"API Error: {error_text}")
                    return "Sorry, an error occurred."
    except Exception as e:
        print(f"Exception in process_response: {str(e)}")  # Debug output
        st.error(f"Connection error: {str(e)}")
        return "Sorry, I couldn't establish a connection to the API."


st.set_page_config(
    page_title="Clever Assistant",
    page_icon="🔥",
    layout="wide"
)

st.title("Your clever assistant. 🤓")

# Initialize session state
init_session_state()

# Sidebar with information
with st.sidebar:
    st.markdown("""
    ### 💡 About the Assistant

    This AI-powered Assistant helps you with:
    - 📖 Access your internal documents
    - ☁️ Lookup weather information

    Just ask your questions!
    """)

# Chat container
chat_container = st.container()

# Display messages
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Input field
if prompt := st.chat_input("Your question..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # Process API response
        response = asyncio.run(process_response(prompt))
        message_placeholder.markdown(response)

        # Update chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown("*Powered by Datamics*")

#Start frontend with streamlit run frontend/app.py
