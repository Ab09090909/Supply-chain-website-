import streamlit as st
import requests

def render_chatbot_button():
    """Renders the Open Chat button at the top of the page."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    
    if not st.session_state.chatbot_visible:
        if st.button("💬 Open Chat", key="top_chat_button", type="primary"):
            st.session_state.chatbot_visible = True
            st.rerun()

def render_chatbot_window():
    """Renders the floating chat window."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chatbot_visible:
        return

    # CSS for floating chat window
    st.markdown("""
    <style>
    .chat-window-container {
        position: fixed;
        top: 80px;
        right: 20px;
        width: 400px;
        max-width: 90vw;
        max-height: 70vh;
        background-color: #1a1d29;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.6);
        border: 1px solid #2E86C1;
        z-index: 9999;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #2E86C1 0%, #1a5276 100%);
        color: white;
        padding: 15px 20px;
        font-size: 18px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-subtitle {
        color: #d0e8f5;
        font-size: 12px;
        margin-top: 3px;
    }
    
    .chat-messages {
        background-color: #0f1117;
        padding: 15px;
        height: 400px;
        overflow-y: auto;
        flex-grow: 1;
    }
    
    .chat-messages::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-messages::-webkit-scrollbar-track {
        background: #1a1d29;
        border-radius: 10px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: #2E86C1;
        border-radius: 10px;
    }
    
    .chat-input-area {
        padding: 15px;
        background-color: #1a1d29;
        border-top: 1px solid #2E86C1;
    }
    
    .close-chat-btn {
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        padding: 5px 15px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
    }
    
    .close-chat-btn:hover {
        background: rgba(255,0,0,0.6);
    }
    </style>
    
    <div class="chat-window-container">
        <div class="chat-header">
            <div>
                <div>💬 EthioChain AI</div>
                <div class="chat-subtitle">English / አማርኛ</div>
            </div>
            <button class="close-chat-btn" onclick="document.getElementById('close_chat_hidden').click()">❌</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hidden button to close chat
    if st.button("", key="close_chat_hidden", type="secondary"):
        st.session_state.chatbot_visible = False
        st.rerun()
    
    # Chat messages area
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    role = st.session_state.get("role", "customer")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)
    if prompt := st.chat_input("Ask me...", key="chat_input_field"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_response(prompt, role)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.markdown('</div>', unsafe_allow_html=True)

def get_response(prompt, role):
    """Calls Groq API with detailed system instructions."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "️ GROQ_API_KEY not found in secrets."
    
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
                return f"️ API Error {resp.status_code}: {resp.text}"
            
        return resp.json()["choices"][0]["message"]["content"]
        
    except requests.exceptions.Timeout:
        return "⚠️ Request timeout. Please try again."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
