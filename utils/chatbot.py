import streamlit as st
import requests
from utils.ai_instructions import get_system_prompt

def render_chatbot():
    """Renders the floating chat icon and the pop-up chat card."""
    
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # CSS Styles
    st.markdown("""
    <style>
    .chat-fab-wrapper {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
    }
    
    .chat-popup-card {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        width: 350px;
        max-width: 90vw;
        background-color: #0f1117;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.6);
        border: 1px solid #2a2d36;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    
    .chat-header-blue {
        background-color: #2E86C1;
        color: white;
        padding: 15px 20px;
        font-size: 18px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 12px 12px 0 0;
    }
    
    .chat-history-container {
        background-color: #1a1d29;
        margin: 10px 15px;
        padding: 15px;
        min-height: 250px;
        max-height: 350px;
        overflow-y: auto;
        border-radius: 8px;
        border: 1px solid #2a2d36;
    }
    
    .chat-input-container {
        margin: 0 15px 15px 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state.chatbot_visible:
        if st.button("", key="fab_open_chat", help="Open Chat Assistant"):
            st.session_state.chatbot_visible = True
            st.rerun()
        return

    # Render chat popup card
    st.markdown('<div class="chat-popup-card">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="chat-header-blue"><span>💬 EthioChain AI</span></div>', unsafe_allow_html=True)
    
    # Subtitle and Exit button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption("English / አማርኛ")
    with col2:
        if st.button("❌", key="chat_exit_btn", help="Close chat"):
            st.session_state.chatbot_visible = False
            st.rerun()
            
    # Chat history container
    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
    role = st.session_state.get("role", "customer")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input container
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    if prompt := st.chat_input("Ask me...", key="chat_input_field"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = _get_groq_response(prompt, role)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def _get_groq_response(prompt: str, role: str) -> str:
    """Calls the Groq API to get the AI response."""
    api_key = st.secrets.get("GROQ_API_KEY")
    
    if not api_key:
        return """**⚠️ Groq API Key Not Configured**

To enable the AI chatbot, you need to add your Groq API key to Streamlit secrets:

1. Go to your Streamlit Cloud dashboard
2. Click "Manage app" -> "Secrets"
3. Add this line:
