import streamlit as st
import requests
from datetime import datetime

# 🛡️ API Keys (Replace with your actual keys)
GROQ_API_KEY = "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"
NEWS_API_KEY = "2a85b7ff3378486fb4c8f553b07351f0"

# Page Config
st.set_page_config(page_title="💬 AI Chatbot", page_icon="🤖", layout="centered")

# Background Styling
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

# Sidebar Feedback
st.sidebar.markdown("### 📊 Feedback")
sidebar_feedback = st.sidebar.radio("How was the response?", ["Bad", "OK", "Good", "Very Good", "Best"], index=2)

# Session initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback_score" not in st.session_state:
    st.session_state.feedback_score = 0
if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 512

# 📰 Get Latest News Function
@st.cache_data(ttl=86400)
def get_latest_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}&pageSize=5"
    try:
        res = requests.get(url).json()
        articles = res.get("articles", [])
        news_list = [f"- {a['title']} ({a['source']['name']})" for a in articles]
        return "\n".join(news_list)
    except Exception as e:
        return f"⚠️ Error fetching news: {e}"

# News Section
st.markdown("### 📰 Latest News (India)")
news_summary = get_latest_news()
st.markdown(f"<div style='background-color: rgba(255,255,255,0.1); padding:10px; border-radius:10px; color:white;'>{news_summary}</div>", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center; color: white;'>💬 MindEase AI Chatbot</h1>", unsafe_allow_html=True)

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input and Bot response
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Inject news context into prompt
    context = f"Today is {datetime.today().strftime('%A, %B %d, %Y')}.\nHere are some latest news headlines from India:\n{news_summary}\n\nUser asked: {prompt}"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_option,
        "messages": [{"role": "user", "content": context}],
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

        # Feedback Logic
        fb = sidebar_feedback
        if fb == "Bad":
            st.session_state.feedback_score -= 1
            st.session_state.max_tokens = max(256, st.session_state.max_tokens - 64)
        elif fb == "OK":
            st.session_state.feedback_score -= 0.5
        elif fb == "Good":
            st.session_state.feedback_score += 1
            st.session_state.max_tokens += 32
        elif fb == "Very Good":
            st.session_state.feedback_score += 2
            st.session_state.max_tokens += 48
        elif fb == "Best":
            st.session_state.feedback_score += 3
            st.session_state.max_tokens += 64

        st.toast(f"🧠 Feedback: {fb} | 🎯 Score: {st.session_state.feedback_score} | 🔧 Tokens: {st.session_state.max_tokens}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
