import streamlit as st
import requests
from utils.ai_instructions import get_system_prompt

def render_chatbot():
    """Renders a compact, floating AI chatbot with an exit button."""
    
    # Initialize session state for chatbot visibility
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = True
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # CSS for the compact floating chatbot
    st.markdown("""
    <style>
    /* Floating Container - Bottom Right */
    .chatbot-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        width: 320px;
    }
    /* The Chat Box - Reduced Height */
    .chat-box {
        background-color: #1a1d29;
        border: 1px solid #2E86C1;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        overflow: hidden;
        max-height: 350px; /* Reduced height */
        display: flex;
        flex-direction: column;
    }
    /* Header with Exit Button */
    .chat-header {
        background-color: #2E86C1;
        color: white;
        padding: 10px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: bold;
    }
    .exit-btn {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        font-weight: bold;
    }
    .exit-btn:hover {
        color: #ffcccc;
    }
    /* Chat Messages Area */
    .chat-messages {
        padding: 10px;
        overflow-y: auto;
        flex-grow: 1;
        max-height: 200px; /* Limit message area height */
        background-color: #0f1117;
    }
    /* Input Area */
    .chat-input-area {
        padding: 10px;
        background-color: #1a1d29;
        border-top: 1px solid #2E86C1;
        display: flex;
        gap: 5px;
    }
    /* Hide Streamlit default chat input styling inside our custom div */
    .chat-input-area .stTextInput > div > div > input {
        background-color: #2a2d36;
        color: white;
        border-radius: 20px;
        padding: 5px 15px;
    }
    /* Open Button (when closed) */
    .open-chat-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        background-color: #2E86C1;
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .open-chat-btn:hover {
        background-color: #1a5276;
    }
    </style>
    """, unsafe_allow_html=True)

    # If chatbot is closed, show the open button
    if not st.session_state.chatbot_visible:
        st.markdown('<button class="open-chat-btn" onclick="alert(\'Streamlit does not support direct JS onclick, please use the button below\')">💬</button>', unsafe_allow_html=True)
        if st.button("💬 Open Chat", key="open_chat_fab"):
            st.session_state.chatbot_visible = True
            st.rerun()
        return

    # If chatbot is open, show the compact box
    st.markdown('<div class="chatbot-container"><div class="chat-box">', unsafe_allow_html=True)
    
    # Header with Exit Button
    st.markdown("""
    <div class="chat-header">
        <span>💬 EthioChain AI</span>
    </div>
    """, unsafe_allow_html=True)
    
    # We use a form or button to handle the exit since we can't use JS onclick easily in Streamlit
    # We'll place the exit button logic here using Streamlit's button but styled via CSS if possible, 
    # or just a standard button at the top. For simplicity and reliability in Streamlit:
    
    # Actually, let's use a Streamlit button for the exit to ensure it works perfectly
    # We will render it inside the container using columns
    
    # Messages Area
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    role = st.session_state.get("role", "customer")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input Area
    st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)
    
    # We need to put the exit button and input in the same row. 
    # Since we are using raw HTML/CSS wrappers, we will use Streamlit columns inside the wrapper.
    # Note: Streamlit elements inside raw HTML divs can sometimes behave oddly, 
    # so we will close the HTML divs and use Streamlit's native layout for the controls, 
    # but style them to look like they are inside the box.
    
    st.markdown('</div></div></div>', unsafe_allow_html=True) # Close chat-input-area, chat-box, chatbot-container
    
    # Now render the actual interactive Streamlit elements below the visual box, 
    # but we will use negative margins or just place them logically.
    # Actually, the best way in Streamlit is to use `st.container` and style it.
    
    # Let's use a simpler, 100% reliable Streamlit-native approach for the compact chatbot:
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.caption("💬 EthioChain AI Assistant (English / አማርኛ)")
        with col2:
            if st.button("❌ Exit", key="exit_chatbot", help="Close chatbot"):
                st.session_state.chatbot_visible = False
                st.rerun()
                
        # Chat history
        chat_container = st.container(height=200, border=True)
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
        # Input
        if prompt := st.chat_input("Ask me...", key="chatbot_input"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message immediately
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
            # Get AI response
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = _get_openrouter_response(prompt, role)
                        st.markdown(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})

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
        return f"⚠️ Error connecting to AI: {str(e)}"
