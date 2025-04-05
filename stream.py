import streamlit as st
import requests
from datetime import datetime
import json
import os
import pandas as pd
import matplotlib.pyplot as plt

# API Keys
GROQ_API_KEY = "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"
NEWS_API_KEY = "2a85b7ff3378486fb4c8f553b07351f0"
SERP_API_KEY = "f70b86191f72adcb577d5868de844c8ad9c9a684db77c939448bcbc1ffaa7bb7"

# Background Image
bg_url = "https://images.unsplash.com/photo-1604079629440-18cdd197c3bd?auto=format&fit=crop&w=1950&q=80"

st.set_page_config(page_title="💬 AI ChatApp", layout="centered")

st.markdown(f"""
    <style>
        body, .stApp {{
            background-image: url('{bg_url}');
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
        .stMarkdown, .stTextInput>div>div>input, .stButton button {{
            color: #dff6ff !important;
        }}
    </style>
""", unsafe_allow_html=True)

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

# Session states
if "messages" not in st.session_state: st.session_state.messages = []
if "feedback_score" not in st.session_state: st.session_state.feedback_score = 0
if "max_tokens" not in st.session_state: st.session_state.max_tokens = 512
if "last_response" not in st.session_state: st.session_state.last_response = ""
if "last_prompt" not in st.session_state: st.session_state.last_prompt = ""

# Feedback
st.sidebar.title("📥 Feedback")
feedback_labels = {
    "Bad": "😠 Bad", "OK": "😐 OK", "Good": "🙂 Good", "Very Good": "😄 Very Good", "Best": "🤩 Best"
}
feedback = st.sidebar.radio("Rate last response", list(feedback_labels.values()), index=None)
if feedback and st.session_state.last_prompt:
    label = {v: k for k, v in feedback_labels.items()}[feedback]
    adjust = {"Bad": -1, "OK": -0.5, "Good": 1, "Very Good": 2, "Best": 3}.get(label, 0)
    st.session_state.feedback_score += adjust
    st.session_state.max_tokens = max(128, min(2048, st.session_state.max_tokens + int(adjust * 32)))
    entry = {
        "timestamp": str(datetime.now()),
        "user_input": st.session_state.last_prompt,
        "response": st.session_state.last_response,
        "feedback": label,
        "score": st.session_state.feedback_score
    }
    os.makedirs("feedback_logs", exist_ok=True)
    with open("feedback_logs/feedback.json", "a") as f: f.write(json.dumps(entry) + "\n")
    st.sidebar.success(f"Feedback saved: {label}")

# Title
st.markdown("<h1 style='text-align: center; color: white;'>💬 AI ChatApp</h1>", unsafe_allow_html=True)

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Input
prompt = st.chat_input("Ask anything...")
if prompt:
    st.session_state.last_prompt = prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    bot_reply = None
    if "news" in prompt.lower():
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        res = requests.get(url).json()
        if "articles" in res:
            bot_reply = "📰 **Top Headlines:**\n" + "\n\n".join([f"- {a['title']}" for a in res["articles"][:5]])
    else:
        serp_url = f"https://serpapi.com/search.json?q={prompt}&api_key={SERP_API_KEY}"
        serp_data = requests.get(serp_url).json()
        if "answer_box" in serp_data:
            box = serp_data["answer_box"]
            bot_reply = box.get("answer") or box.get("snippet") or box.get("title")
        elif "organic_results" in serp_data:
            bot_reply = serp_data["organic_results"][0].get("snippet", "No snippet found.")
        else:
            bot_reply = None

    if not bot_reply:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": model_option,
            "messages": st.session_state.messages,
            "max_tokens": st.session_state.max_tokens,
            "stream": False
        }
        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            result = res.json()
            bot_reply = result["choices"][0]["message"]["content"]
        except Exception as e:
            bot_reply = f"⚠️ Error: {e}"

    st.session_state.last_response = bot_reply
    with st.chat_message("assistant"): st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
