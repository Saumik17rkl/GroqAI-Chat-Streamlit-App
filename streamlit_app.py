import streamlit as st
from typing import Generator
from groq import Groq

# Page configuration
st.set_page_config(page_icon="💬", layout="wide", page_title="AIChat App")

# Display page icon
def icon(emoji: str):
    st.write(f'<span style="font-size: 78px; line-height: 1">{emoji}</span>', unsafe_allow_html=True)

icon("🏎️")
st.subheader("AI Chat App", divider="rainbow", anchor=False)

# Groq API client (hardcoded API key - replace with your key)
client = Groq(api_key="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")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# Model options (mixtral removed)
models = {
    "gemma2-9b-it": {"name": "Gemma2-9b-it", "tokens": 8192, "developer": "Google"},
    "llama-3.3-70b-versatile": {"name": "LLaMA3.3-70b-versatile", "tokens": 128000, "developer": "Meta"},
    "llama-3.1-8b-instant": {"name": "LLaMA3.1-8b-instant", "tokens": 128000, "developer": "Meta"},
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
}

# Layout for model selection
model_option = st.selectbox(
    "Choose a model:",
    options=list(models.keys()),
    format_func=lambda x: models[x]["name"],
    index=4
)

# Reset messages on model change
if st.session_state.selected_model != model_option:
    st.session_state.messages = []
    st.session_state.selected_model = model_option

# Default max tokens (fixed)
max_tokens = 4096

# Show chat history
for message in st.session_state.messages:
    avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Streaming generator
def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Chat input
if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar='👨‍💻'):
        st.markdown(prompt)

    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            max_tokens=max_tokens,
            stream=True
        )

        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)

        # Store the response
        if isinstance(full_response, str):
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            combined_response = "\n".join(str(item) for item in full_response)
            st.session_state.messages.append({"role": "assistant", "content": combined_response})

    except Exception as e:
        st.error(e, icon="🚨")

# ---------------- Sidebar Feedback Section ----------------
with st.sidebar:
    st.markdown("## 🌟 We'd Love Your Feedback!")
    st.markdown("Help us improve this chat app. How was your experience?")
    
    feedback = st.radio(
        "Rate your experience:",
        ["👍 Excellent", "🙂 Good", "😐 Okay", "👎 Needs Improvement"],
        horizontal=True
    )

    comment = st.text_area("💬 Additional Comments", placeholder="Tell us what we can do better...")

    if st.button("Submit Feedback"):
        st.success("✅ Thank you for your feedback!")
        # Save to file or database if needed
