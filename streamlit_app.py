import streamlit as st
import requests
import random

# 🛡️ HARD-CODED API KEY (Not recommended for production)
GROQ_API_KEY = "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"

# Page Config
st.set_page_config(page_title="💬 AI Chatbot", page_icon="🤖", layout="centered")

# Background & Style
st.markdown("""
    <style>
        body, .stApp {
            background-image: url('https://wallpapercave.com/wp/FjnZ25X.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        .stChatMessage {
            background-color: rgba(135, 206, 250, 0.4) !important; /* Sky Blue transparent */
            border-radius: 12px;
            padding: 10px;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

# Model Mapping
models = {
    "gemma2-9b-it": "Gemma2-9b-it",
    "llama-3.3-70b-versatile": "LLaMA3.3-70b",
    "llama-3.1-8b-instant": "LLaMA3.1-8b",
    "llama3-70b-8192": "LLaMA3-70b",
    "llama3-8b-8192": "LLaMA3-8b",
}

# Sidebar - Model Selection and Chat Clear
st.sidebar.title("⚙️ Settings")
model_option = st.sidebar.selectbox("Choose a model:", list(models.keys()), format_func=lambda x: models[x])
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []

# Sidebar - Feedback System
st.sidebar.subheader("🧠 Chatbot Feedback & Learning")

# Feedback state
if "confidence_score" not in st.session_state:
    st.session_state.confidence_score = 70
if "feedback_data" not in st.session_state:
    st.session_state.feedback_data = {"positive": 0, "negative": 0, "neutral": 0, "comments": []}

rating = st.sidebar.radio("How was the last response?", ["Bad", "Okay", "Good", "Very Good", "Best"], index=None)

if rating:
    if rating in ["Bad", "Okay"]:
        st.session_state.feedback_data["negative"] += 1
        delta = -random.randint(1, 5)
        st.sidebar.warning("We'll improve based on your feedback!")
    else:
        st.session_state.feedback_data["positive"] += 1
        delta = random.randint(1, 4)
        st.sidebar.success("Glad you liked it!")

    st.session_state.confidence_score = min(100, max(0, st.session_state.confidence_score + delta))

    comment = st.sidebar.text_input("Any suggestions or comments?")
    if st.sidebar.button("Submit Feedback"):
        if comment:
            st.session_state.feedback_data["comments"].append(comment)
        st.sidebar.success("✅ Feedback submitted!")

st.sidebar.subheader("📊 Learning Overview")
st.sidebar.write(f"✅ Positive: {st.session_state.feedback_data['positive']}")
st.sidebar.write(f"❌ Negative: {st.session_state.feedback_data['negative']}")
st.sidebar.write(f"📈 Confidence Score: {st.session_state.confidence_score}%")

if st.session_state.feedback_data["comments"]:
    st.sidebar.write("📝 Recent Comments:")
    for c in st.session_state.feedback_data["comments"][-3:]:
        st.sidebar.caption(f"• {c}")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title
st.markdown("<h1 style='text-align: center; color: white;'>💬 MindEase AI Chatbot</h1>", unsafe_allow_html=True)

# Show previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"<div class='stChatMessage'>{msg['content']}</div>", unsafe_allow_html=True)

# New user input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<div class='stChatMessage'>{prompt}</div>", unsafe_allow_html=True)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_option,
        "messages": st.session_state.messages,
        "max_tokens": 512,
        "stream": False
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        result = response.json()
        bot_reply = result["choices"][0]["message"]["content"]

        with st.chat_message("assistant"):
            st.markdown(f"<div class='stChatMessage'>{bot_reply}</div>", unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
