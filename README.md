# Neurochat Chat Streamlit App

## Overview
Groq Chat is a Streamlit-based chatbot application that allows users to interact with various AI models, including Google's Gemma and Meta's LLaMA. The app provides an intuitive interface for real-time chat, model selection, and dynamic token allocation.

## Features
- 💬 **Real-time Chat**: Interact with AI models seamlessly.
- 🏎️ **Multiple Models**: Choose from models like Gemma2-9b-it, LLaMA3 variants, and Mixtral.
- 🎛️ **Dynamic Token Allocation**: Adjust max tokens based on the selected model.
- ⚡ **Session Management**: Maintains chat history and clears it when switching models.
- 🔥 **Stream Responses**: Generates responses dynamically using Groq API.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Saumik17rkl/GroqAI-Chat-Streamlit-App.git
   cd GroqAI-Chat-Streamlit-App
   ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up API key:
   - Create a `.streamlit/secrets.toml` file.
   - Add your Groq API key:
     ```toml
     [secrets]
     GROQ_API_KEY = "your-api-key-here"
     ```

## Usage
Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

## Models Available
| Model Name | Tokens | Developer |
|------------|--------|------------|
| Gemma2-9b-it | 8192 | Google |
| LLaMA3.3-70b-versatile | 128000 | Meta |
| LLaMA3.1-8b-instant | 128000 | Meta |
| LLaMA3-70b-8192 | 8192 | Meta |
| LLaMA3-8b-8192 | 8192 | Meta |
| Mixtral-8x7b-Instruct-v0.1 | 32768 | Mistral |

## Contributing
Feel free to fork this repository and submit pull requests for enhancements.


