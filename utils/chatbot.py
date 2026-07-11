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
    """Renders the floating chat window with working buttons."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chatbot_visible:
        return

    role = st.session_state.get("role", "customer")
    
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
        background: linear-gradient(135deg, #1a1d29 0%, #0f1117 100%);
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.7);
        border: 2px solid #2E86C1;
        z-index: 9999;
        overflow: hidden;
        animation: slideIn 0.3s ease-out;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chat-header {
        background: linear-gradient(135deg, #2E86C1 0%, #1a5276 100%);
        color: white;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .chat-title {
        font-size: 18px;
        font-weight: bold;
    }
    .chat-subtitle {
        font-size: 12px;
        color: #d0e8f5;
        margin-top: 3px;
    }
    .chat-messages {
        background: #0f1117;
        padding: 15px;
        height: 350px;
        overflow-y: auto;
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
        background: #1a1d29;
        border-top: 1px solid #2E86C1;
    }
    </style>
    
    <div class="chat-window-container">
        <div class="chat-header">
            <div>
                <div class="chat-title">💬 EthioChain AI</div>
                <div class="chat-subtitle">English / አማርኛ</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for header buttons
    header_col1, header_col2 = st.columns([5, 1])
    
    with header_col2:
        # Exit button
        if st.button("❌", key="close_chat_btn", help="Close chat"):
            st.session_state.chatbot_visible = False
            st.rerun()
    
    role = st.session_state.get("role", "customer")
    
    # Chat messages area
    st.markdown('<div style="background: #0f1117; border-radius: 12px; margin: 10px 0;">', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin: 10px 0; padding: 0 15px;">
                <div style="background: #2E86C1; color: white; padding: 10px 15px; border-radius: 18px 18px 4px 18px; max-width: 80%; word-wrap: break-word;">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin: 10px 0; padding: 0 15px;">
                <div style="background: #2a2d36; color: #e8eaed; padding: 10px 15px; border-radius: 18px 18px 18px 4px; max-width: 80%; word-wrap: break-word;">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input form
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input("", placeholder="Ask me...", label_visibility="collapsed", key="chat_input")
        with col2:
            send_clicked = st.form_submit_button("Send", use_container_width=True)
    
    # Process message
    if send_clicked and user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        with st.spinner("Thinking..."):
            response = get_response(user_input, role)
        
        # Add assistant response
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Rerun to show new messages
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
