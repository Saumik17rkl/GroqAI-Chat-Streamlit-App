import streamlit as st
from typing import Generator
from groq import Groq
import base64

# Page configuration
st.set_page_config(page_icon="💬", layout="wide", page_title="AIChat App")

# Custom background with dark sky and stars
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiApmHMIA0hjFFtAI4rKOOrAZF7EBeFU942bHDViiy9CBZmAkR2GCvO7tEy9InU27kVwuJWRWZj8Dcr7ciWy5XW2w_6nFnagZxQsfbpg5pTVrEti4GB7_27TRddJUC97p1fGw6l0-RGWpE/s1600/night-sky-wallpaper-1920x1080-mountain-hd-1875-wallpaper-high.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
[data-testid="stChatInput"] textarea {{
    background-color: black !important;
    border: 2px solid #444 !important;
    color: white !important;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Display page icon and title
st.markdown("""
<div style='text-align: center; font-size: 78px;'>🏎️</div>
<h2 style='text-align: center;'>Groq Chat Streamlit App</h2>
<hr style='border: 1px solid #fff;'>
""", unsafe_allow_html=True)

# Groq API client with direct key (replace with your real API key)
client = Groq(api_key="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")  # Replace with your actual API key

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# Sidebar: Choose a model
with st.sidebar:
    st.markdown("""
    <h3 style='text-align:center;'>🤖 Choose a Model</h3>
    """, unsafe_allow_html=True)
    models = {
        "gemma2-9b-it": {"name": "Gemma2-9b-it", "tokens": 8192, "developer": "Google"},
        "llama-3.3-70b-versatile": {"name": "LLaMA3.3-70b-versatile", "tokens": 128000, "developer": "Meta"},
        "llama-3.1-8b-instant": {"name": "LLaMA3.1-8b-instant", "tokens": 128000, "developer": "Meta"},
        "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
        "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    }
    model_option = st.selectbox(
        "Choose a model:",
        options=list(models.keys()),
        format_func=lambda x: models[x]["name"],
        index=4
    )

    if st.session_state.selected_model != model_option:
        st.session_state.messages = []
        st.session_state.selected_model = model_option

    st.markdown("""
    <hr>
    <h3 style='text-align:center;'>💡 Feedback Corner</h3>
    <p style='text-align:center;'>We value your thoughts. Help us improve!</p>
    """, unsafe_allow_html=True)
    feedback = st.text_area("📝 Leave your feedback here:")
    if st.button("📩 Submit Feedback"):
        st.success("Thanks for your feedback! 🌟")

# Show messages
for message in st.session_state.messages:
    avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
    bubble_color = "rgba(0, 123, 255, 0.2)"  # Slightly transparent blue
    alignment = "flex-end" if message["role"] == "user" else "flex-start"
    border_radius = "20px 20px 0 20px" if message["role"] == "user" else "20px 20px 20px 0"

    st.markdown(f"""
    <div style="display: flex; justify-content: {alignment}; margin: 10px 0;">
        <div style="
            background-color: {bubble_color};
            color: black;
            padding: 10px 15px;
            border-radius: {border_radius};
            max-width: 70%;
            box-shadow: 0px 0px 5px rgba(0,0,0,0.3);
        ">
            <strong>{avatar}</strong> {message["content"]}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Generator for streaming
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
            max_tokens=2048,
            stream=True
        )

        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)

        if isinstance(full_response, str):
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            combined_response = "\n".join(str(item) for item in full_response)
            st.session_state.messages.append({"role": "assistant", "content": combined_response})

    except Exception as e:
        st.error(e, icon="🚨")
