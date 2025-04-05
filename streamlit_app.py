import streamlit as st
from typing import Generator
from groq import Groq
from datetime import datetime

# Page configuration
st.set_page_config(page_icon="💬", layout="wide", page_title="AIChat App")

# Initialize Groq API client with your API key
client = Groq(api_key="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")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemma2-9b-it"

# Sidebar: Choose a model
with st.sidebar:
    st.markdown("<h3 style='text-align:center;'>🤖 Choose a Model</h3>", unsafe_allow_html=True)
    models = {
        "gemma2-9b-it": {"name": "Gemma2-9b-it", "tokens": 8192, "developer": "Google", "description": "Google’s fast and efficient 9B model, great for quick queries."},
        "llama-3.3-70b-versatile": {"name": "LLaMA3.3-70b-versatile", "tokens": 128000, "developer": "Meta", "description": "Versatile 70B model from Meta – suitable for complex tasks and longer context."},
        "llama-3.1-8b-instant": {"name": "LLaMA3.1-8b-instant", "tokens": 128000, "developer": "Meta", "description": "Lightweight, instant response model. Great for real-time chat."},
        "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta", "description": "High-performance model, best for deep contextual understanding."},
        "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta", "description": "Fast and cost-efficient, great for short and focused replies."},
    }
    model_option = st.selectbox(
        "Choose a model:",
        options=list(models.keys()),
        format_func=lambda x: f"{models[x]['name']} - {models[x]['description']}",
        index=0
    )

    if st.session_state.selected_model != model_option:
        st.session_state.messages = []
        st.session_state.selected_model = model_option

# Display chat messages
for message in st.session_state.messages:
    is_user = message["role"] == "user"
    avatar_url = "https://img.icons8.com/ios-filled/50/user-male-circle.png" if is_user else "https://img.icons8.com/ios-filled/50/bot.png"
    st.chat_message(
        avatar=avatar_url,
        message=message["content"],
        is_user=is_user
    )

# Function to generate responses
def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Input message box
user_input = st.text_input("You:", "")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    response_container = st.empty()
    prompt = f"User: {user_input}\nAI: "
    response_container.markdown(prompt)

    try:
        chat_completion = client.chat.completions.stream.create(
            model=model_option,
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            max_tokens=2048
        )

        response = ""
        for chunk in generate_chat_responses(chat_completion):
            response += chunk
            response_container.markdown(prompt + response)

        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"An error occurred: {e}")
