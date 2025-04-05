import streamlit as st
import requests
from datetime import datetime

# ✅ Must be first Streamlit command
st.set_page_config(page_title="🌍AI ChatApp", layout="centered")

# 🎨 Background Styling
background_image_url = "https://images.unsplash.com/photo-1513151233558-d860c5398176?auto=format&fit=crop&w=1950&q=80"
st.markdown(f'''
    <style>
    .stApp {{
        background-image: url("{background_image_url}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
    }}
    .stChatMessage {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        border-radius: 12px;
        padding: 10px;
    }}
    .stMarkdown, .stTextInput input, .stButton button, .stSelectbox>div>div {{
        color: white !important;
   ''' }}
    </style>
, unsafe_allow_html=True)

# ⚠️ Hardcoded API KEYS (For Demo Only)
GROQ_API_KEY = "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"
NEWS_API_KEY = "2a85b7ff3378486fb4c8f553b07351f0"
SERPAPI_KEY = "f70b86191f72adcb577d5868de844c8ad9c9a684db77c939448bcbc1ffaa7bb7"

# Get latest headlines
@st.cache_data(ttl=86400)
def fetch_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}&pageSize=5"
        res = requests.get(url).json()
        return [f"- {a['title']} ({a['source']['name']})" for a in res.get("articles", [])]
    except:
        return ["⚠️ Unable to fetch latest news."]

# Web Search for query
def web_search(query):
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

# Title
st.title("🧠 News-Aware Chatbot")

# Sidebar Settings
st.sidebar.title("⚙️ Settings")
model_option = st.sidebar.selectbox("Choose Model", ["llama3-8b-8192", "gemma2-9b-it"])
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.messages = []

# Feedback system
feedback = st.sidebar.radio("🗣️ How was the response?", ["Bad", "OK", "Good", "Very Good", "Best"], index=2)

# Init session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show latest news
st.markdown("### 📢 Latest Headlines")
headlines = fetch_news()
st.markdown("\n".join(headlines))

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask anything..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Real-time context
    news_summary = "\n".join(headlines)
    web_snip = web_search(prompt)

    context = f"""You are a smart assistant aware of real-time news and internet updates.
    
    🗓️ Date: {datetime.today().strftime('%A, %B %d, %Y')}
    📰 Top News:
    {news_summary}
    
    🌐 Web Info:
    {web_snip}
    
    User asked: {prompt}
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

    st.toast(f"✅ Feedback: {feedback}")
