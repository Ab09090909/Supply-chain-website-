import streamlit as st
import requests

def render_chatbot():
    """Renders the floating AI chatbot with fixed position."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # CSS for fixed floating button and chat interface
    st.markdown("""
    <style>
    /* Make the button container float fixed at bottom-right */
    div[data-testid="stHorizontalBlock"] > div:has(button[kind="secondary"][data-testid="baseButton-secondary"]) {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 9999 !important;
    }
    
    /* Style the AI Assistant button to look like a pill */
    button[kind="secondary"][data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #2E86C1 0%, #1a5276 100%) !important;
        color: white !important;
        border: none !important;
        padding: 15px 25px !important;
        border-radius: 50px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(46, 134, 193, 0.4) !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    
    button[kind="secondary"][data-testid="baseButton-secondary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(46, 134, 193, 0.6) !important;
    }
    
    /* Chat popup card */
    .chat-popup-card {
        position: fixed;
        bottom: 90px;
        right: 20px;
        z-index: 9999;
        width: 350px;
        max-width: 90vw;
        max-height: 60vh;
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
        color: #d0e8f5;
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
    </style>
    """, unsafe_allow_html=True)

    # If closed, show the floating "AI Assistant" button
    if not st.session_state.chatbot_visible:
        # Use a real Streamlit button — this is the only way clicks work reliably
        if st.button("💬 AI Assistant", key="fab_open_chat", type="secondary"):
            st.session_state.chatbot_visible = True
            st.rerun()
        return

    # Chat interface is open — render the popup card
    st.markdown('<div class="chat-popup-card">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="chat-header">
        <div>💬 EthioChain AI</div>
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
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.chat_history.append({"role": "user", "content": prompt})
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_response(prompt, role)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Keep the "AI Assistant" button visible at the bottom even when chat is open
    if st.button("💬 AI Assistant", key="fab_close_chat", type="secondary"):
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
