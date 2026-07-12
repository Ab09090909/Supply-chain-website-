import streamlit as st
import requests

def render_chatbot():
    """Renders the floating AI chatbot at the bottom of the screen."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # CSS for floating chatbot at bottom
    st.markdown("""
    <style>
    /* Floating chat container - fixed at bottom right */
    .floating-chat-container {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        width: 350px !important;
        max-width: 90vw !important;
        z-index: 9999 !important;
    }
    
    /* Chat window styling */
    .chat-window {
        background: linear-gradient(135deg, #1a1d29 0%, #0f1117 100%);
        border-radius: 16px;
        border: 2px solid #2E86C1;
        box-shadow: 0 10px 40px rgba(0,0,0,0.7);
        overflow: hidden;
        margin-bottom: 10px;
    }
    
    /* Chat header */
    .chat-header {
        background: #2E86C1;
        color: white;
        padding: 12px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-title {
        font-size: 16px;
        font-weight: bold;
    }
    
    .chat-subtitle {
        font-size: 11px;
        color: #d0e8f5;
    }
    
    /* Chat messages area */
    .chat-messages {
        height: 300px;
        overflow-y: auto;
        padding: 15px;
        background: #0f1117;
    }
    
    .chat-messages::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: #2E86C1;
        border-radius: 10px;
    }
    
    /* Exit button */
    .exit-btn {
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .exit-btn:hover {
        background: rgba(255,0,0,0.6);
    }
    
    /* Floating open button */
    .open-chat-btn {
        background: linear-gradient(135deg, #2E86C1 0%, #1a5276 100%);
        color: white;
        border: none;
        padding: 15px 25px;
        border-radius: 50px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(46, 134, 193, 0.4);
        display: flex;
        align-items: center;
        gap: 10px;
        width: 100%;
    }
    
    .open-chat-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 134, 193, 0.6);
    }
    
    /* Input area */
    .chat-input-area {
        padding: 15px;
        background: #1a1d29;
        border-top: 1px solid #2E86C1;
    }
    </style>
    """, unsafe_allow_html=True)

    # If chatbot is closed, show floating open button at bottom
    if not st.session_state.chatbot_visible:
        st.markdown("""
        <div class="floating-chat-container">
            <button class="open-chat-btn" onclick="document.getElementById('open_chat_hidden').click()">
                <span>💬</span>
                <span>AI Assistant</span>
            </button>
        </div>
        """, unsafe_allow_html=True)
        
        # Hidden button to trigger open
        if st.button("", key="open_chat_hidden", type="secondary"):
            st.session_state.chatbot_visible = True
            st.rerun()
        return

    # Chatbot is open - show floating window at bottom
    st.markdown("""
    <div class="floating-chat-container">
        <div class="chat-window">
            <div class="chat-header">
                <div>
                    <div class="chat-title">💬 EthioChain AI</div>
                    <div class="chat-subtitle">English / አማርኛ</div>
                </div>
                <button class="exit-btn" onclick="document.getElementById('close_chat_hidden').click()">✕</button>
            </div>
            <div class="chat-messages">
    """, unsafe_allow_html=True)
    
    # Display chat messages
    role = st.session_state.get("role", "customer")
    
    if not st.session_state.chat_history:
        st.markdown('<div style="text-align: center; color: #666; padding: 20px;">Welcome! Ask me anything about EthioChain supply chain.</div>', unsafe_allow_html=True)
    
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
                <div style="background: #2E86C1; color: white; padding: 10px 15px; border-radius: 18px 18px 4px 18px; max-width: 80%; word-wrap: break-word;">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
                <div style="background: #2a2d36; color: #e8eaed; padding: 10px 15px; border-radius: 18px 18px 18px 4px; max-width: 80%; word-wrap: break-word;">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input area
    st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)
    
    if prompt := st.chat_input("Type your message...", key="chat_input"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.rerun()
    
    st.markdown('</div></div></div>', unsafe_allow_html=True)
    
    # Hidden button to close chat
    if st.button("", key="close_chat_hidden", type="secondary"):
        st.session_state.chatbot_visible = False
        st.rerun()

def get_response(prompt, role):
    """Calls Groq API with detailed system instructions."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "⚠️ GROQ_API_KEY not found in secrets."
    
    system_prompt = f"""You are EthioChain AI, the official intelligent assistant for the EthioChain commercial supply chain platform in Ethiopia. 

STRICT RULES:
1. CURRENCY: ALWAYS quote all prices and financial figures in Ethiopian Birr (ETB) using comma separators (e.g., ETB 15,000.00). NEVER use USD, EUR, or any other currency.
2. LANGUAGE: You are fully bilingual in English and Amharic (አማርኛ). Detect the language the user is typing in and respond in that exact language.
3. SCOPE: Only answer questions related to the Ethiopian supply chain, agriculture, manufacturing, commerce, logistics, and the EthioChain platform features. Politely decline to answer unrelated questions.
4. TONE: Professional, helpful, concise, and encouraging.
5. PLATFORM NAVIGATION: If a user asks how to do something on the platform, guide them to the correct tab (e.g., "To add a product, please go to your Inventory tab").

USER ROLE CONTEXT:
The current user is logged in as a: {role}.
- If Producer: Help them with inventory management, understanding demand forecasts, and finding merchants.
- If Merchant: Help them browse the marketplace, check supplier fraud risks, and find reliable producers.
- If Customer: Help them find products, understand recommendations, and manage their favorites.
- If Admin: Help them with platform oversight, user management, and system health.

If the user greets you, welcome them warmly and briefly list 2-3 ways you can help them based on their role."""

    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in st.session_state.chat_history[-8:]:
        if "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
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
