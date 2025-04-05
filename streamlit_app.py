import streamlit as st
import requests

# 🛡️ API Key (hardcoded for testing; do not use in production)
GROQ_API_KEY = "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"

# Page Config
st.set_page_config(page_title="💬 AI Chatbot", page_icon="🤖", layout="centered")

# Background and Chat Styling
st.markdown("""
    <style>
        body, .stApp {
            background-image: url('https://wallpapercave.com/wp/FjnZ25X.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: center;
        }
        .stChatMessage {
            background-color: rgba(135, 206, 250, 0.05) !important;
            border-radius: 12px;
            padding: 10px;
            color: #dff6ff;
        }
        .stMarkdown, .stTextInput>div>div>input, .stButton button, .stSelectbox>div>div>div {
            color: #dff6ff !important;
        }
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

# Sidebar feedback section
st.sidebar.markdown("### 📊 Feedback")
sidebar_feedback = st.sidebar.radio("How was the response?",
                                    ["Bad", "OK", "Good", "Very Good", "Best"],
                                    index=2,  # Default to "Good"
                                    key="sidebar_feedback")

# Session initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback_score" not in st.session_state:
    st.session_state.feedback_score = 0
if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 512

# Title
st.markdown("<h1 style='text-align: center; color: white;'>💬 MindEase AI Chatbot</h1>", unsafe_allow_html=True)

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input area
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare API request
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

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        # Feedback system based on sidebar input
        feedback = sidebar_feedback

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

        st.toast(f"🧠 Feedback: {feedback} | 🎯 Score: {st.session_state.feedback_score} | 🔧 Tokens: {st.session_state.max_tokens}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
