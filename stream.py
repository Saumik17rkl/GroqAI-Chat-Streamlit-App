import streamlit as st
import requests
from datetime import datetime
import json
import os

# API Keys (hardcoded for testing only)
GROQ_API_KEY = "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"

# Background Image URL
background_image_url = "https://images.unsplash.com/photo-1604079629440-18cdd197c3bd?auto=format&fit=crop&w=1950&q=80"

# Page Config
st.set_page_config(page_title="💬 MindEase AI Chatbot", page_icon="🤖", layout="centered")

# Background and Styling
st.markdown(f"""
    <style>
        body, .stApp {{
            background-image: url('{background_image_url}');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: #dff6ff;
        }}
        .stChatMessage {{
            background-color: rgba(135, 206, 250, 0.15) !important;
            border-radius: 12px;
            padding: 10px;
            color: #dff6ff;
        }}
        .stMarkdown, .stTextInput>div>div>input, .stButton button, .stSelectbox>div>div>div {{
            color: #dff6ff !important;
        }}
    </style>
""", unsafe_allow_html=True)

# Models dictionary
models = {
    "gemma2-9b-it": "Gemma2-9b-it",
    "llama-3.3-70b-versatile": "LLaMA3.3-70b",
    "llama-3.1-8b-instant": "LLaMA3.1-8b",
    "llama3-70b-8192": "LLaMA3-70b",
    "llama3-8b-8192": "LLaMA3-8b",
}

# Sidebar
st.sidebar.title("⚙️ Settings")
model_option = st.sidebar.selectbox("Choose a model:", list(models.keys()), format_func=lambda x: models[x])
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.session_state.feedback_score = 0
    st.session_state.max_tokens = 512

# Feedback Graph Placeholder
st.sidebar.title("\U0001f4ca Feedback Analytics")
st.sidebar.markdown("Score: **{}**".format(st.session_state.get("feedback_score", 0)))

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback_score" not in st.session_state:
    st.session_state.feedback_score = 0
if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 512

# Title
st.markdown("<h1 style='text-align: center; color: white;'>💬 MindEase AI Chatbot</h1>", unsafe_allow_html=True)

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # API request
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_option,
        "messages": st.session_state.messages,
        "max_tokens": st.session_state.max_tokens,
        "stream": False
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        result = response.json()
        bot_reply = result["choices"][0]["message"]["content"]

        with st.chat_message("assistant"):
            st.markdown(bot_reply)

            feedback = st.radio("How was the response?", ["Bad", "OK", "Good", "Very Good", "Best"], key=f"feedback_{len(st.session_state.messages)}")
            if feedback:
                if feedback == "Bad":
                    st.session_state.feedback_score -= 1
                    st.session_state.max_tokens = max(256, st.session_state.max_tokens - 64)
                elif feedback == "OK":
                    st.session_state.feedback_score -= 0.5
                elif feedback == "Good":
                    st.session_state.feedback_score += 1
                    st.session_state.max_tokens += 32
                elif feedback == "Very Good":
                    st.session_state.feedback_score += 2
                    st.session_state.max_tokens += 48
                elif feedback == "Best":
                    st.session_state.feedback_score += 3
                    st.session_state.max_tokens += 64

                feedback_entry = {
                    "timestamp": str(datetime.now()),
                    "user_input": prompt,
                    "response": bot_reply,
                    "feedback": feedback,
                    "score": st.session_state.feedback_score
                }
                os.makedirs("feedback_logs", exist_ok=True)
                with open("feedback_logs/feedback.json", "a") as f:
                    f.write(json.dumps(feedback_entry) + "\n")

                st.toast(f"🧠 Feedback: {feedback} | 🎯 Score: {st.session_state.feedback_score} | 🔧 Tokens: {st.session_state.max_tokens}")

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
