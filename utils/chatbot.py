import streamlit as st
import requests

def render_chatbot_tab():
    """Renders the AI chatbot as a fixed-position tab with half height."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # CSS for fixed position chat window (ONLY HEIGHT REDUCED)
    st.markdown("""
    <style>
    .fixed-chat-container {
        position: fixed !important;
        top: 100px !important;
        right: 20px !important;
        width: 350px !important;
        height: 350px !important; /* REDUCED: Fixed half height */
        max-height: 350px !important;
        z-index: 9998 !important;
        background: linear-gradient(135deg, #1a1d29 0%, #0f1117 100%) !important;
        border-radius: 12px !important;
        border: 2px solid #2E86C1 !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.7) !important;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: column !important;
    }
    
    .fixed-chat-header {
        background: #2E86C1 !important;
        color: white !important;
        padding: 10px 15px !important;
        flex-shrink: 0 !important;
    }
    
    .fixed-chat-title {
        font-size: 16px !important;
        font-weight: bold !important;
        margin: 0 !important;
    }
    
    .fixed-chat-subtitle {
        font-size: 11px !important;
        color: #d0e8f5 !important;
        margin-top: 3px !important;
    }
    
    .fixed-chat-messages {
        height: 180px !important; /* REDUCED: Half of 400px */
        overflow-y: auto !important;
        padding: 10px !important;
        background: #0f1117 !important;
        flex-grow: 1 !important;
    }
    
    .fixed-chat-messages::-webkit-scrollbar {
        width: 5px !important;
    }
    
    .fixed-chat-messages::-webkit-scrollbar-thumb {
        background: #2E86C1 !important;
        border-radius: 10px !important;
    }
    
    .fixed-chat-input {
        padding: 10px !important;
        background: #1a1d29 !important;
        border-top: 1px solid #2E86C1 !important;
        flex-shrink: 0 !important;
    }
    
    .clear-btn {
        background: rgba(255,255,255,0.2) !important;
        color: white !important;
        border: none !important;
        padding: 5px 10px !important;
        border-radius: 5px !important;
        cursor: pointer !important;
        font-size: 12px !important;
    }
    
    .clear-btn:hover {
        background: rgba(255,0,0,0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="fixed-chat-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="fixed-chat-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="fixed-chat-title">💬 EthioChain AI</div>
                <div class="fixed-chat-subtitle">English / አማርኛ</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Clear button row
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🗑️ Clear", key="clear_chat_fixed", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    role = st.session_state.get("role", "customer")
    
    # Chat messages area
    st.markdown('<div class="fixed-chat-messages">', unsafe_allow_html=True)
    
    if not st.session_state.chat_history:
        st.markdown('<div style="text-align: center; color: #666; padding: 10px; font-size: 13px;">👋 Welcome! Ask me anything.</div>', unsafe_allow_html=True)
    
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin: 5px 0;">
                <div style="background: #2E86C1; color: white; padding: 8px 12px; border-radius: 14px 14px 2px 14px; max-width: 90%; word-wrap: break-word; font-size: 13px;">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin: 5px 0;">
                <div style="background: #2a2d36; color: #e8eaed; padding: 8px 12px; border-radius: 14px 14px 14px 2px; max-width: 90%; word-wrap: break-word; font-size: 13px;">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown('<div class="fixed-chat-input">', unsafe_allow_html=True)
    
    if prompt := st.chat_input("Type message...", key="fixed_chat_input"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)

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
                return f"⚠️ API Error {resp.status_code}: {resp.text}"
            
        return resp.json()["choices"][0]["message"]["content"]
        
    except requests.exceptions.Timeout:
        return "️ Request timeout. Please try again."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
