import streamlit as st
import requests
from datetime import datetime
import json
import os

# API Keys
GROQ_API_KEY = "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"
NEWS_API_KEY = "2a85b7ff3378486fb4c8f553b07351f0"
SERP_API_KEY = "f70b86191f72adcb577d5868de844c8ad9c9a684db77c939448bcbc1ffaa7bb7"

# Page Setup
st.set_page_config(page_title="💬 AI ChatApp", layout="centered")
bg_url = "https://images.unsplash.com/photo-1604079629440-18cdd197c3bd?auto=format&fit=crop&w=1950&q=80"
st.markdown(f"""
    <style>
        .stApp {{
            background-image: url('{bg_url}');
            background-size: cover;
            background-attachment: fixed;
        }}
        .stChatMessage {{
            background-color: rgba(0, 0, 0, 0.2) !important;
            color: white !important;
        }}
    </style>
""", unsafe_allow_html=True)

# Sidebar Settings
st.sidebar.title("⚙️ Settings")
models = {
    "gemma2-9b-it": "Gemma2-9b-it",
    "llama-3.3-70b-versatile": "LLaMA3.3-70b",
    "llama-3.1-8b-instant": "LLaMA3.1-8b",
    "llama3-70b-8192": "LLaMA3-70b",
    "llama3-8b-8192": "LLaMA3-8b",
}
model_option = st.sidebar.selectbox("Choose Model", list(models.keys()), format_func=lambda x: models[x])

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "feedback_score" not in st.session_state: st.session_state.feedback_score = 0
if "max_tokens" not in st.session_state: st.session_state.max_tokens = 512
if "last_response" not in st.session_state: st.session_state.last_response = ""
if "last_prompt" not in st.session_state: st.session_state.last_prompt = ""

# Clear Button
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.messages.clear()

# Feedback Section
st.sidebar.title("📥 Feedback")
feedback_labels = {"Bad": "😠", "OK": "😐", "Good": "🙂", "Very Good": "😄", "Best": "🤩"}
feedback = st.sidebar.radio("How was the last response?", list(feedback_labels.values()), index=None)
if feedback and st.session_state.last_prompt:
    reverse_map = {v: k for k, v in feedback_labels.items()}
    label = reverse_map[feedback]
    adjust = {"Bad": -1, "OK": -0.5, "Good": 1, "Very Good": 2, "Best": 3}.get(label, 0)
    st.session_state.feedback_score += adjust
    st.session_state.max_tokens = max(128, min(2048, st.session_state.max_tokens + int(adjust * 32)))
    os.makedirs("feedback_logs", exist_ok=True)
    with open("feedback_logs/feedback.json", "a") as f:
        f.write(json.dumps({
            "timestamp": str(datetime.now()),
            "user_input": st.session_state.last_prompt,
            "response": st.session_state.last_response,
            "feedback": label,
            "score": st.session_state.feedback_score
        }) + "\n")
    st.sidebar.success(f"Saved: {label}")

# Title
st.markdown("<h1 style='text-align: center; color: white;'>🤖 AI ChatApp</h1>", unsafe_allow_html=True)

# Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# User Prompt
prompt = st.chat_input("Ask anything about the world, tech, news, or more...")
if prompt:
    st.session_state.last_prompt = prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # Try SERPAPI first
    try:
        serp_url = f"https://serpapi.com/search.json?q={prompt}&api_key={SERP_API_KEY}"
        serp_data = requests.get(serp_url).json()

        bot_reply = ""
        if "answer_box" in serp_data:
            abox = serp_data["answer_box"]
            bot_reply = f"### 📌 Quick Answer:\n**{abox.get('answer') or abox.get('snippet') or abox.get('title')}**\n"
            if abox.get("snippet_highlighted_words"):
                bot_reply += "\n🔍 Highlights:\n" + "\n".join([f"- {w}" for w in abox["snippet_highlighted_words"]])
        elif "organic_results" in serp_data:
            results = serp_data["organic_results"][:3]
            bot_reply = "### 🌐 Search Summary:\n"
            for r in results:
                title = r.get("title", "No Title")
                snippet = r.get("snippet", "")
                link = r.get("link", "#")
                bot_reply += f"- **[{title}]({link})**\n  {snippet}\n\n"
        else:
            bot_reply = None
    except Exception as e:
        bot_reply = f"⚠️ Could not retrieve search data: {e}"

    # Fallback to LLM if SERP fails or weak result
    if not bot_reply or len(bot_reply.strip()) < 30:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": model_option,
            "messages": st.session_state.messages,
            "max_tokens": st.session_state.max_tokens
        }
        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            result = res.json()
            core_reply = result["choices"][0]["message"]["content"]
            bot_reply = f"### 🤖 Here's What I Found:\n{core_reply.strip()}\n\n✅ _Generated using {models[model_option]}_"
        except Exception as e:
            bot_reply = f"❌ Error using LLM: {e}"

    st.session_state.last_response = bot_reply
    with st.chat_message("assistant"): st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
