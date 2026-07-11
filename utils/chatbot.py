import streamlit as st
import requests


def render_chatbot():
    """Renders the floating AI chatbot."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # CSS with fixed scrolling
    st.markdown("""
    <style>
    .chat-popup-card {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        width: 350px;
        max-width: 90vw;
        max-height: 80vh;
        background-color: #0f1117;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.6);
        border: 1px solid #2a2d36;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .chat-header {
        background-color: #2E86C1;
        color: white;
        padding: 15px 20px;
        font-size: 18px;
        font-weight: bold;
        flex-shrink: 0;
    }
    
    .chat-subtitle {
        color: #a0a0a0;
        font-size: 12px;
        margin-top: 5px;
    }
    
    .chat-history-container {
        background-color: #1a1d29;
        margin: 10px 15px;
        padding: 15px;
        height: 300px;
        overflow-y: auto;
        overflow-x: hidden;
        border-radius: 8px;
        border: 1px solid #2a2d36;
        flex-grow: 1;
    }
    
    .chat-history-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-history-container::-webkit-scrollbar-track {
        background: #1a1d29;
        border-radius: 10px;
    }
    
    .chat-history-container::-webkit-scrollbar-thumb {
        background: #2E86C1;
        border-radius: 10px;
    }
    
    .chat-input-container {
        margin: 0 15px 15px 15px;
        flex-shrink: 0;
    }
    
    .exit-btn {
        float: right;
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
    }
    
    .exit-btn:hover {
        background: rgba(255,0,0,0.6);
    }
    </style>
    """, unsafe_allow_html=True)

    # Show open button if closed
    if not st.session_state.chatbot_visible:
        if st.button("💬 Chat", key="fab_open_chat"):
            st.session_state.chatbot_visible = True
            st.rerun()
        return

    # Chat interface
    st.markdown('<div class="chat-popup-card">', unsafe_allow_html=True)
    
    # Header with Exit button
    st.markdown("""
    <div class="chat-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>💬 EthioChain AI</span>
        </div>
        <div class="chat-subtitle">English / አማርኛ</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Exit button
    if st.button("❌ Exit", key="chat_exit_btn"):
        st.session_state.chatbot_visible = False
        st.rerun()
            
    role = st.session_state.get("role", "customer")
    
    # Chat history with independent scroll
    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)
            
    # Chat input
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    if prompt := st.chat_input("Ask me...", key="chat_input_field"):
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
            
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_response(prompt, role)
                st.markdown(response)
                # Add assistant response to history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def get_response(prompt, role):
    """Calls Groq API to get AI response."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "⚠️ GROQ_API_KEY not found in secrets."
    
    # Build messages array properly
    messages = [
        {"role": "system", "content": f"You are EthioChain AI, an assistant for an Ethiopian agricultural supply chain platform. The user role is: {role}. Always quote prices in ETB."}
    ]
    
    # Add chat history
    for msg in st.session_state.chat_history[-10:]:
        if "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Ensure messages alternate properly
    cleaned_messages = [messages[0]]
    for i in range(1, len(messages)):
        if messages[i]["role"] != messages[i-1]["role"]:
            cleaned_messages.append(messages[i])
        else:
            cleaned_messages[-1]["content"] += "\n" + messages[i]["content"]
    
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + api_key.strip(),
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": cleaned_messages,
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if resp.status_code != 200:
            try:
                error_data = resp.json()
                error_msg = error_data.get("error", {}).get("message", resp.text)
                return f"⚠️ API Error {resp.status_code}: {error_msg}"
            except:
                return f"⚠️ API Error {resp.status_code}: {resp.text}"
            
        return resp.json()["choices"][0]["message"]["content"]
        
    except requests.exceptions.Timeout:
        return "⚠️ Request timeout. Please try again."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
