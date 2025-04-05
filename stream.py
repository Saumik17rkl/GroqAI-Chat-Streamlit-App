import streamlit as st
import requests
import speech_recognition as sr
import pyttsx3
from datetime import datetime

# Set page config
st.set_page_config(page_title="🌍 AI ChatApp", layout="centered")

# Dark/Light theme toggle
theme = st.sidebar.radio("🎨 Theme", ["Dark", "Light"])
dark_mode = theme == "Dark"

background_url = "https://images.unsplash.com/photo-1513151233558-d860c5398176?auto=format&fit=crop&w=1950&q=80" if dark_mode else ""
text_color = "white" if dark_mode else "black"
bg_color = "rgba(0,0,0,0.5)" if dark_mode else "rgba(255,255,255,0.6)"

# Custom CSS
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url('{background_url}');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
        color: {text_color};
    }}
    .stTextInput > div > div > input,
    .stChatMessage {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
        border-radius: 10px;
    }}
    .stButton > button {{
        background-color: rgba(255, 255, 255, 0.1);
        color: {text_color};
        border-radius: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# API keys (For demo only)
GROQ_API_KEY = "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"
NEWS_API_KEY = "2a85b7ff3378486fb4c8f553b07351f0"
SERPAPI_KEY = "f70b86191f72adcb577d5868de844c8ad9c9a684db77c939448bcbc1ffaa7bb7"

@st.cache_data(ttl=86400)
def fetch_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}&pageSize=5"
        res = requests.get(url).json()
        return [f"- {a['title']} ({a['source']['name']})" for a in res.get("articles", [])]
    except:
        return ["⚠️ Unable to fetch latest news."]

def web_search(query):
    try:
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google",
        }
        url = "https://serpapi.com/search"
        res = requests.get(url, params=params).json()
        if "answer_box" in res:
            return res["answer_box"].get("snippet") or res["answer_box"].get("answer")
        elif "organic_results" in res and res["organic_results"]:
            return res["organic_results"][0].get("snippet", "")
        else:
            return "🌐 No web data found."
    except:
        return "❌ Error during web search."

# 🎤 Voice Input
def voice_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Speak now...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "⚠️ Could not understand audio."
        except sr.RequestError:
            return "❌ Speech recognition service failed."

# 🔊 Text-to-Speech Output
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    engine.say(text)
    engine.runAndWait()

# Title
st.title("🧠 Voice & News-Aware Chatbot")

# Sidebar
st.sidebar.title("⚙️ Settings")
model_option = st.sidebar.selectbox("Choose Model", ["llama3-8b-8192", "gemma2-9b-it"])
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.messages = []

# Chat History Init
if "messages" not in st.session_state:
    st.session_state.messages = []

# Latest News
st.markdown("### 📢 Latest Headlines")
headlines = fetch_news()
st.markdown("\n".join(headlines))

# Show old chats
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 👂 Input
col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.chat_input("Type or speak your question...")

with col2:
    if st.button("🎤 Speak"):
        user_input = voice_to_text()
        st.success(f"You said: {user_input}")

# 🔄 Processing
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Real-time context
    news_summary = "\n".join(headlines)
    web_snip = web_search(user_input)
    context = f"""You are a smart assistant aware of real-time news and internet updates.

🗓️ Date: {datetime.today().strftime('%A, %B %d, %Y')}
📰 Top News:
{news_summary}

🌐 Web Info:
{web_snip}

User asked: {user_input}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_option,
        "messages": [{"role": "user", "content": context}],
        "max_tokens": 512,
        "stream": False
    }

    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        bot_reply = res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        bot_reply = f"❌ Error: {e}"

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # 🔊 Read aloud
    if st.toggle("🔊 Enable Voice Output", value=True):
        speak(bot_reply)

    # 💾 Save to File
    if st.toggle("💾 Save chat to file", value=False):
        with open("chat_history.txt", "w", encoding="utf-8") as f:
            for msg in st.session_state.messages:
                f.write(f"{msg['role'].capitalize()}: {msg['content']}\n")
        st.success("✅ Chat saved to chat_history.txt")
