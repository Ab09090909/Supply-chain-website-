import streamlit as st
import requests

def render_chatbot_tab():
    """Renders the AI chatbot as a fixed-position tab with half size."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # CSS for fixed position chat window (HALF SIZE)
    st.markdown("""
    <style>
    .fixed-chat-container {
        position: fixed !important;
        top: 100px !important;
        right: 20px !important;
        width: 250px !important; /* Reduced from 400px */
        max-width: 90vw !important;
        max-height: 50vh !important; /* Reduced from 70vh */
        z-index: 9998 !important;
        background: linear-gradient(135deg, #1a1d29 0%, #0f1117 100%) !important;
        border-radius: 12px !important;
        border: 2px solid #2E86C1 !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.7) !important;
        overflow: hidden !important;
    }
    
    .fixed-chat-header {
        background: #2E86C1 !important;
        color: white !important;
        padding: 10px 12px !important; /* Reduced padding */
    }
    
    .fixed-chat-title {
        font-size: 14px !important; /* Reduced font size */
        font-weight: bold !important;
        margin: 0 !important;
    }
    
    .fixed-chat-subtitle {
        font-size: 10px !important; /* Reduced font size */
        color: #d0e8f5 !important;
        margin-top: 2px !important;
    }
    
    .fixed-chat-messages {
        height: 150px !important; /* Reduced from 400px */
        overflow-y: auto !important;
        padding: 10px !important;
        background: #0f1117 !important;
    }
    
    .fixed-chat-messages::-webkit-scrollbar {
        width: 4px !important;
    }
    
    .fixed-chat-messages::-webkit-scrollbar-thumb {
        background: #2E86C1 !important;
        border-radius: 10px !important;
    }
    
    .fixed-chat-input {
        padding: 10px !important;
        background: #1a1d29 !important;
        border-top: 1px solid #2E86C1 !important;
    }
    
    .clear-btn {
        background: rgba(255,255,255,0.2) !important;
        color: white !important;
        border: none !important;
        padding: 4px 8px !important;
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
        if st.button("️ Clear", key="clear_chat_fixed", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    role = st.session_state.get("role", "customer")
    
    # Chat messages area
    st.markdown('<div class="fixed-chat-messages">', unsafe_allow_html=True)
    
    if not st.session_state.chat_history:
        st.markdown('<div style="text-align: center; color: #666; padding: 10px; font-size: 12px;"> Welcome! Ask me anything.</div>', unsafe_allow_html=True)
    
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin: 5px 0;">
                <div style="background: #2E86C1; color: white; padding: 6px 10px; border-radius: 12px 12px 2px 12px; max-width: 90%; word-wrap: break-word; font-size: 12px;">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin: 5px 0;">
                <div style="background: #2a2d36; color: #e8eaed; padding: 6px 10px; border-radius: 12px 12px 12px 2px; max-width: 90%; word-wrap: break-word; font-size: 12px;">
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
