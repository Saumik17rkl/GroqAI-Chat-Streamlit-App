import streamlit as st

# Page configuration
st.set_page_config(page_icon="💬", layout="wide", page_title="AIChat App")

# Minimized page background image
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://wallpapercave.com/wp/FjnZ25X.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}
[data-testid="stChatInput"] textarea {
    background-color: black !important;
    border: 2px solid #444 !important;
    color: white !important;
}
textarea {
    border: 2px solid green !important;
    padding: 8px !important;
    border-radius: 6px !important;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; font-size: 78px;'>🏎️</div>
<h2 style='text-align: center; color: white;'>Groq Chat Streamlit App</h2>
<hr style='border: 1px solid #fff;'>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemma2-9b-it"

# Sidebar: Choose a model
with st.sidebar:
    st.markdown("<h3 style='text-align:center;'>🤖 Choose a Model</h3>", unsafe_allow_html=True)
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
        index=0
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
        st.session_state.feedback = feedback
        st.success("Thanks for your feedback! 🌟")
        # Here you can add reinforcement learning logic to train the model based on feedback
        # Example: Send feedback to your backend for further processing

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

# Chat input
if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar='👨‍💻'):
        st.markdown(prompt)

    try:
        # Simulate chat completion response (you will need to replace this with actual API call)
        response = f"Response to: {prompt}"
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(e, icon="🚨")
