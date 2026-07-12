import streamlit as st
import requests

def render_chatbot():
    """Renders the AI Assistant with a truly floating window."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # CSS to make the chat window float
    st.markdown("""
    <style>
    /* Target the column containing the chat input and make it float */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stChatInput"]) {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        width: 400px !important;
        max-width: 90vw !important;
        max-height: 600px !important;
        background: linear-gradient(135deg, #1a1d29 0%, #0f1117 100%) !important;
        border-radius: 16px !important;
        border: 2px solid #2E86C1 !important;
        z-index: 9999 !important;
        padding: 20px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.7) !important;
        overflow-y: auto !important;
        display: flex !important;
        flex-direction: column !important;
    }
    
    /* Style the buttons inside the floating window */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stChatInput"]) button[kind="secondary"] {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stChatInput"]) button[kind="secondary"]:hover {
        background: rgba(255,0,0,0.3) !important;
    }
    
    /* Hide the default Streamlit chat input container border */
    div[data-testid="stChatInput"] {
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # If chatbot is closed, show the floating open button
    if not st.session_state.chatbot_visible:
        # This button will also be targeted by CSS if we wanted, but let's keep it simple
        st.markdown("""
        <style>
        /* Make the open button float too */
        div[data-testid="stVerticalBlock"] > div:has(button[kind="primary"][aria-label="Open Chat"]) {
            position: fixed !important;
            bottom: 20px !important;
            right: 20px !important;
            z-index: 9999 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💬 AI Assistant", key="open_chat_btn", type="primary", use_container_width=True):
                st.session_state.chatbot_visible = True
                st.rerun()
        return

    # Chatbot is open - render the floating window content
    # The CSS above will automatically make this column float
    
    # Header with Clear and Exit buttons
    title_col, btn_col1, btn_col2 = st.columns([3, 1, 1])

    with title_col:
        st.markdown("<h3 style='color: #2E86C1; margin-top: 0; margin-bottom: 5px;'>💬 EthioChain AI</h3>", unsafe_allow_html=True)
        st.caption("English / አማርኛ")

    with btn_col1:
        if st.button("🗑️ Clear", key="clear_chat_btn", use_container_width=True, help="Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()

    with btn_col2:
        if st.button("❌ Exit", key="close_chat_btn", use_container_width=True, help="Close chat"):
            st.session_state.chatbot_visible = False
            st.rerun()

    st.markdown("---")
    
    role = st.session_state.get("role", "customer")
    
    # Chat messages area (fixed height inside the floating window)
    chat_container = st.container(height=350)
    
    with chat_container:
        if not st.session_state.chat_history:
            st.info(" Welcome! Ask me anything about EthioChain supply chain.")
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input (The CSS targets this to make the whole column float)
    if prompt := st.chat_input("Type your message...", key="chat_input"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_response(prompt, role)
                    st.markdown(response)
        
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
