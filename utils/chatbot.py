import streamlit as st
import requests
from utils.ai_instructions import get_system_prompt

def render_chatbot():
    """Renders the floating chat icon and the pop-up chat card."""
    
    # Initialize session state
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Inject CSS for the floating button and the pop-up card
    st.markdown("""
    <style>
    /* 1. Floating Action Button (FAB) */
    .chat-fab-wrapper {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
    }
    
    /* 2. The Pop-up Card Container */
    .chat-popup-card {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        width: 350px;
        background-color: #0f1117; /* Dark background */
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.6);
        border: 1px solid #2a2d36;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    
    /* 3. Blue Header Styling */
    .chat-header-blue {
        background-color: #2E86C1; /* Exact blue from image */
        color: white;
        padding: 15px 20px;
        font-size: 18px;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 10px;
        border-radius: 12px 12px 0 0;
    }
    
    /* 4. Chat History Box Styling */
    .chat-history-container {
        background-color: #1a1d29;
        border-radius: 8px;
        margin: 10px 15px;
        padding: 10px;
        min-height: 200px;
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #2a2d36;
    }
    
    /* 5. Input Area Styling */
    .chat-input-container {
        margin: 0 15px 15px 15px;
    }
    /* Force the chat input to look like the image (dark rounded box) */
    .chat-input-container div[data-baseweb="base-input"] {
        background-color: #1a1d29 !important;
        border-radius: 20px !important;
        border: 1px solid #2a2d36 !important;
    }
    .chat-input-container input {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- LOGIC: If chatbot is CLOSED, show the floating icon ---
    if not st.session_state.chatbot_visible:
        st.markdown('<div class="chat-fab-wrapper">', unsafe_allow_html=True)
        # Use a standard button, but the CSS wrapper will help position it if we used JS. 
        # Since we can't use JS onclick easily, we place it at the bottom and rely on the user scrolling, 
        # OR we use a placeholder. For simplicity and reliability, we'll just use a button here.
        # To make it truly float without JS, we'd need an iframe, but this is the standard Streamlit way.
        if st.button("💬", key="fab_open_chat", help="Open Chat Assistant"):
            st.session_state.chatbot_visible = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # --- LOGIC: If chatbot is OPEN, show the Pop-up Card ---
    st.markdown('<div class="chat-popup-card">', unsafe_allow_html=True)
    
    # 1. Blue Header
    st.markdown('<div class="chat-header-blue">💬 EthioChain AI</div>', unsafe_allow_html=True)
    
    # 2. Subtitle and Exit Button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("💬 EthioChain AI Assistant (English / አማርኛ)")
    with col2:
        if st.button("❌ Exit", key="chat_exit_btn", use_container_width=True):
            st.session_state.chatbot_visible = False
            st.rerun()
            
    # 3. Chat History Box
    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
    role = st.session_state.get("role", "customer")
    
    # Display history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 4. Input Area
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    if prompt := st.chat_input("Ask me...", key="chat_input_field"):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = _get_openrouter_response(prompt, role)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
    st.markdown('</div>', unsafe_allow_html=True) # Close input container
    st.markdown('</div>', unsafe_allow_html=True) # Close popup card

def _get_openrouter_response(prompt: str, role: str) -> str:
    """Calls the OpenRouter API to get the AI response."""
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if not api_key:
        return "️ AI Assistant is currently unavailable (API key missing)."
        
    system_prompt = get_system_prompt(role)
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(st.session_state.chat_history[-10:])
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://ethiochain.streamlit.app",
                "X-Title": "EthioChain Assistant"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct:free", 
                "messages": messages
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
