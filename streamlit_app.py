import streamlit as st
from groq import Groq
import os

# Set page config and background
st.set_page_config(page_title="Groq Chat - WhatsApp Style", layout="wide")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("https://wallpapercave.com/wp/FjnZ25X.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Groq client setup
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Sidebar - Model Selection
st.sidebar.title("🤖 Select LLM Model")
model = st.sidebar.selectbox(
    "Choose a model:",
    ["llama3-8b", "llama3-70b"],
    index=1
)

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main chat input/output
st.title("💬 Groq Chat (WhatsApp Style)")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    messages=st.session_state.messages,
                    model=model,
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"⚠️ Error: {e}"

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

    # Feedback section
    with st.expander("📝 Give Feedback on this response"):
        feedback = st.radio("Was this response helpful?", ("👍 Yes", "👎 No"), horizontal=True)
        comment = st.text_area("Any comments or suggestions?", key=f"fb_{len(st.session_state.messages)}")
        if st.button("Submit Feedback", key=f"submit_{len(st.session_state.messages)}"):
            st.success("Thanks for your feedback!")

