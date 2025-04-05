import streamlit as st
from typing import Generator
from groq import Groq

# Page configuration
st.set_page_config(page_icon="💬", layout="wide", page_title="Meta AI Chat")

# WhatsApp-style UI CSS
st.markdown("""
    <style>
        .stChatMessage {
            border-radius: 18px;
            padding: 10px 15px;
            max-width: 70%;
            margin: 5px;
            display: inline-block;
        }
        .stChatMessage.user {
            background-color: #dcf8c6;
            margin-left: auto;
            text-align: right;
        }
        .stChatMessage.assistant {
            background-color: #f1f0f0;
            margin-right: auto;
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)

# Icon & Title
st.markdown("<h1 style='text-align: center;'>🤖 Meta AI WhatsApp Style</h1>", unsafe_allow_html=True)

# Groq API client
client = Groq(api_key="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")

# Initialize session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "llama3-8b-8192"

models = {
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
}

model_option = st.sidebar.selectbox("Choose a model:", options=list(models.keys()), format_func=lambda x: models[x]["name"])

if st.session_state.selected_model != model_option:
    st.session_state.messages = []
    st.session_state.selected_model = model_option

# Display messages in chat bubble style
for msg in st.session_state.messages:
    css_class = "user" if msg["role"] == "user" else "assistant"
    st.markdown(f"<div class='stChatMessage {css_class}'>{msg['content']}</div>", unsafe_allow_html=True)

# Streaming function

def generate_response(chat_completion) -> Generator[str, None, None]:
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Input
if prompt := st.chat_input("Type a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"<div class='stChatMessage user'>{prompt}</div>", unsafe_allow_html=True)

    try:
        completion = client.chat.completions.create(
            model=model_option,
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            max_tokens=4096,
            stream=True
        )

        with st.spinner("Meta AI is typing..."):
            stream = generate_response(completion)
            full_reply = st.write_stream(stream)

        if isinstance(full_reply, str):
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
        else:
            combined = "\n".join(str(i) for i in full_reply)
            st.session_state.messages.append({"role": "assistant", "content": combined})

    except Exception as e:
        st.error(f"❌ Error: {e}")

# Sidebar feedback
with st.sidebar:
    st.markdown("## 🌟 Feedback")
    feedback = st.radio("Rate your experience:", ["👍", "🙂", "😐", "👎"], horizontal=True)
    comment = st.text_area("💬 Additional Comments")
    if st.button("Send Feedback"):
        st.success("✅ Feedback submitted! Thank you ✨")
