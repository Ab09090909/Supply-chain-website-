import streamlit as st
import requests

def render_chatbot():
    """Renders the AI Assistant button at top, or full chat window when open."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # If chatbot is closed, show the button at top
    if not st.session_state.chatbot_visible:
        st.markdown("""
        <style>
        .ai-button-container {
            margin: 20px 0;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💬 AI Assistant", key="open_chat_btn", type="primary", use_container_width=True):
                st.session_state.chatbot_visible = True
                st.rerun()
        return

    # Chatbot is open - show full chat window
    st.markdown("""
    <style>
    .chat-window {
        background: linear-gradient(135deg, #1a1d29 0%, #0f1117 100%);
        border-radius: 16px;
        border: 2px solid #2E86C1;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 8px 24px rgba(46, 134, 193, 0.3);
    }
    .chat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 15px;
        border-bottom: 1px solid #2E86C1;
    }
    .chat-title {
        font-size: 24px;
        font-weight: bold;
        color: #2E86C1;
    }
    .chat-subtitle {
        color: #a0a0a0;
        font-size: 14px;
        margin-top: 5px;
    }
    </style>
    
    <div class="chat-window">
        <div class="chat-header">
            <div>
                <div class="chat-title">💬 EthioChain AI Assistant</div>
                <div class="chat-subtitle">English / አማርኛ</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Exit button at top right
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("❌ Exit", key="close_chat_btn", use_container_width=True):
            st.session_state.chatbot_visible = False
            st.rerun()
    
    role = st.session_state.get("role", "customer")
    
    # Chat messages area
    chat_container = st.container(height=400, border=True)
    
    with chat_container:
        if not st.session_state.chat_history:
            st.info("👋 Welcome! Ask me anything about EthioChain supply chain.")
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message...", key="chat_input"):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        # Get AI response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_response(prompt, role)
                    st.markdown(response)
        
        # Add assistant response
        st.session_state.chat_history.append({"role": "assistant", "content": response})
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
