import streamlit as st
import requests
from datetime import datetime
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from serpapi import GoogleSearch

# API Keys
GROQ_API_KEY = "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"
NEWS_API_KEY = "2a85b7ff3378486fb4c8f553b07351f0"
SERP_API_KEY = "f70b86191f72adcb577d5868de844c8ad9c9a684db77c939448bcbc1ffaa7bb7"

# Background Image URL
background_image_url = "https://images.unsplash.com/photo-1604079629440-18cdd197c3bd?auto=format&fit=crop&w=1950&q=80"

# Page Config
st.set_page_config(page_title="💬 MindEase AI Chatbot", page_icon=":robot_face:", layout="centered")

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

# Sidebar settings
st.sidebar.title("⚙️ Settings")
model_option = st.sidebar.selectbox("Choose a model:", list(models.keys()), format_func=lambda x: models[x])
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.session_state.feedback_score = 0
    st.session_state.max_tokens = 512

# Session state
if "messages" not in st.session_state: st.session_state.messages = []
if "feedback_score" not in st.session_state: st.session_state.feedback_score = 0
if "max_tokens" not in st.session_state: st.session_state.max_tokens = 512
if "last_response" not in st.session_state: st.session_state.last_response = ""
if "last_prompt" not in st.session_state: st.session_state.last_prompt = ""

# Feedback analytics
st.sidebar.title("📊 Feedback Analytics")
def load_feedback():
    if os.path.exists("feedback_logs/feedback.json"):
        with open("feedback_logs/feedback.json", "r") as f:
            lines = f.readlines()
            return pd.DataFrame([json.loads(line) for line in lines])
    return pd.DataFrame()
df_feedback = load_feedback()
if not df_feedback.empty:
    df_feedback["timestamp"] = pd.to_datetime(df_feedback["timestamp"])
    st.sidebar.line_chart(df_feedback["score"])

# Feedback in Sidebar (Reinforcement Learning based)
st.sidebar.title("📥 Give Feedback")
feedback_labels = {
    "Bad": "😠 Bad",
    "OK": "😐 OK",
    "Good": "🙂 Good",
    "Very Good": "😄 Very Good",
    "Best": "🤩 Best"
}
feedback_options = list(feedback_labels.values())
feedback_mapping = {v: k for k, v in feedback_labels.items()}
feedback = st.sidebar.radio("Rate last response", feedback_options, index=None)

if feedback and st.session_state.last_prompt:
    actual_feedback = feedback_mapping[feedback]
    adjust = {"Bad": -1, "OK": -0.5, "Good": 1, "Very Good": 2, "Best": 3}.get(actual_feedback, 0)
    st.session_state.feedback_score += adjust
    st.session_state.max_tokens = max(128, min(2048, st.session_state.max_tokens + int(adjust * 32)))
    entry = {
        "timestamp": str(datetime.now()),
        "user_input": st.session_state.last_prompt,
        "response": st.session_state.last_response,
        "feedback": actual_feedback,
        "score": st.session_state.feedback_score
    }
    os.makedirs("feedback_logs", exist_ok=True)
    with open("feedback_logs/feedback.json", "a") as f:
        f.write(json.dumps(entry) + "\n")
    st.sidebar.success(f"Feedback saved: {actual_feedback}")

# PDF Export
class PDF(FPDF):
    def header(self): self.set_font("Arial", "B", 12); self.cell(0, 10, "MindEase Chat History", 0, 1, "C")
def export_chat():
    pdf = PDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    for msg in st.session_state.messages:
        pdf.multi_cell(0, 10, f"{msg['role'].capitalize()}: {msg['content']}\n")
    pdf.output("chat_history.pdf")
    return "chat_history.pdf"
if st.sidebar.button("⬇️ Export Chat as PDF"):
    file_path = export_chat()
    with open(file_path, "rb") as f:
        st.sidebar.download_button("Download Chat", f, file_name="chat_history.pdf")

# Estimated Tokens
estimated_tokens = sum(len(msg["content"].split()) for msg in st.session_state.get("messages", []))
st.sidebar.markdown(f"🧪 Estimated Tokens Used: **{estimated_tokens}**")

# Title
st.markdown("<h1 style='text-align: center; color: white;'>💬AI ChatApp</h1>", unsafe_allow_html=True)

# Display old messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Chat input
prompt = st.chat_input("Type your message...")
if prompt:
    st.session_state.last_prompt = prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    live_reply = None
    if "news" in prompt.lower():
        news_url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        news_data = requests.get(news_url).json()
        if news_data.get("articles"):
            live_reply = "📰 **Top Headlines:**\n" + "\n\n".join([f"- {article['title']}" for article in news_data["articles"][:5]])
    elif "search" in prompt.lower():
        search = GoogleSearch({"q": prompt, "api_key": SERP_API_KEY})
        result = search.get_dict()
        if "answer_box" in result:
            live_reply = result["answer_box"].get("answer") or result["answer_box"].get("snippet")
        elif "organic_results" in result:
            live_reply = result["organic_results"][0]["snippet"]

    if live_reply:
        bot_reply = live_reply
    else:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
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
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
            bot_reply = "Sorry, I couldn't fetch a response."

    st.session_state.last_response = bot_reply
    with st.chat_message("assistant"): st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
