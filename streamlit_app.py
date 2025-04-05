import streamlit as st
from typing import Generator
from groq import Groq
from datetime import datetime
import base64
import PyPDF2
from PIL import Image
import io
import os

# Function to encode local image as base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img_base64 = get_base64_image("WhatsApp Image 2025-04-05 at 23.02.01_24eb3a5d.jpg")

st.set_page_config(page_icon="💬", layout="wide", page_title="AIChat App")

# Minimized page background image
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/jpeg;base64,{img_base64}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
[data-testid="stChatInput"] textarea {{
    background-color: black !important;
    border: 2px solid #444 !important;
    color: white !important;
}}
textarea {{
    border: 2px solid green !important;
    padding: 8px !important;
    border-radius: 6px !important;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; font-size: 78px;'>🏎️</div>
<h2 style='text-align: center; color: white;'>Groq Chat Streamlit App</h2>
<hr style='border: 1px solid #fff;'>
""", unsafe_allow_html=True)

client = Groq(api_key="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")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

with st.sidebar:
    st.markdown("""
    <h3 style='text-align:center;'>🤖 Choose a Model</h3>
    """, unsafe_allow_html=True)
    models = {
        "gemma2-9b-it": {"name": "Gemma2-9b-it", "tokens": 8192, "developer": "Google", "description": "Google’s fast and efficient 9B model, great for quick queries."},
        "llama-3.3-70b-versatile": {"name": "LLaMA3.3-70b-versatile", "tokens": 128000, "developer": "Meta", "description": "Versatile 70B model from Meta – suitable for complex tasks and longer context."},
        "llama-3.1-8b-instant": {"name": "LLaMA3.1-8b-instant", "tokens": 128000, "developer": "Meta", "description": "Lightweight, instant response model. Great for real-time chat."},
        "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta", "description": "High-performance model, best for deep contextual understanding."},
        "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta", "description": "Fast and cost-efficient, great for short and focused replies."},
    }
    model_option = st.selectbox(
        "Choose a model:",
        options=list(models.keys()),
        format_func=lambda x: f"{models[x]['name']} - {models[x]['description']}",
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

# Upload file/image/video section
st.sidebar.markdown("""
<hr>
<h3 style='text-align:center;'>📁 Upload Content</h3>
""", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload file (image/pdf/video):", type=["jpg", "jpeg", "png", "pdf", "mp4"])

if uploaded_file:
    file_type = uploaded_file.type
    if "image" in file_type:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.info("Image processing and art conversion features like Ghibli style coming soon... 🎨")
    elif "pdf" in file_type:
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()
        st.text_area("Extracted PDF Text:", pdf_text, height=300)
    elif "video" in file_type:
        st.video(uploaded_file)
        st.warning("Video analysis support is under development. Stay tuned! 🎬")

# Display chat messages
for message in st.session_state.messages:
    is_user = message["role"] == "user"
    avatar_url = "https://img.icons8.com/ios-filled/50/user-male-circle.png" if is_user else "https://img.icons8.com/ios-filled/50/bot.png"
    bubble_color = "#DCF8C6" if is_user else "#FFFFFF"
    alignment = "flex-end" if is_user else "flex-start"
    text_align = "right" if is_user else "left"
    border_radius = "18px 18px 0 18px" if is_user else "18px 18px 18px 0"
    timestamp = datetime.now().strftime("%H:%M")

    st.markdown(f"""
    <div style="display: flex; justify-content: {alignment}; margin: 8px;">
        <img src="{avatar_url}" width="35" height="35" style="border-radius: 50%; margin: 5px;" />
        <div style="
            background-color: {bubble_color};
            padding: 12px 16px;
            border-radius: {border_radius};
            max-width: 65%;
            box-shadow: 0 1px 2px rgba(0,0,0,0.15);
            color: black;
            font-size: 15px;
            line-height: 1.5;
            text-align: {text_align};
        ">
            {message["content"]}
            <div style="text-align: {text_align}; font-size: 11px; color: gray; margin-top: 5px;">{timestamp}</div>
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
        chat_completion = client.chat.completions.stream.create(
            model=model_option,
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            max_tokens=2048
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
