import streamlit as st
import requests

def render_chatbot_tab():
    """Renders the AI chatbot as a fixed-position tab with half height."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # CSS for fixed position chat window
    st.markdown("""
    <style>
    .fixed-chat-container {
        position: fixed !important;
        top: 100px !important;
        right: 20px !important;
        width: 350px !important;
        height: 350px !important;
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
    .fixed-chat-header { background: #2E86C1 !important; color: white !important; padding: 10px 15px !important; flex-shrink: 0 !important; }
    .fixed-chat-title { font-size: 16px !important; font-weight: bold !important; margin: 0 !important; }
    .fixed-chat-subtitle { font-size: 11px !important; color: #d0e8f5 !important; margin-top: 3px !important; }
    .fixed-chat-messages {
        height: 180px !important;
        overflow-y: auto !important;
        padding: 10px !important;
        background: #0f1117 !important;
        flex-grow: 1 !important;
    }
    .fixed-chat-messages::-webkit-scrollbar { width: 5px !important; }
    .fixed-chat-messages::-webkit-scrollbar-thumb { background: #2E86C1 !important; border-radius: 10px !important; }
    .fixed-chat-input { padding: 10px !important; background: #1a1d29 !important; border-top: 1px solid #2E86C1 !important; flex-shrink: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="fixed-chat-container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="fixed-chat-header">
        <div>
            <div class="fixed-chat-title">💬 EthioChain AI</div>
            <div class="fixed-chat-subtitle">English / አማርኛ</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🗑️", key="clear_chat_fixed", help="Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    role = st.session_state.get("role", "customer")
    
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
    st.markdown('<div class="fixed-chat-input">', unsafe_allow_html=True)
    
    if prompt := st.chat_input("Type message...", key="fixed_chat_input"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def get_response(prompt, role):
    """Calls Groq API with strict instructions."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "⚠️ GROQ_API_KEY not found in secrets."
    
    # --- STRICT INSTRUCTIONS FOR GROQ ---
    system_prompt = f"""You are EthioChain AI, an assistant for an Ethiopian supply chain platform.
User Role: {role}

CRITICAL LANGUAGE RULE:
- If the user writes in ENGLISH, you MUST reply 100% in ENGLISH.
- If the user writes in AMHARIC, you MUST reply 100% in AMHARIC.
- NEVER mix languages in a single response.

CURRENCY RULE:
- Always use ETB for prices (e.g., ETB 1,500). Never use USD.

CONTEXT RULE:
- Only discuss Ethiopian agriculture (Teff, Coffee, Sesame), supply chains, and the EthioChain platform.
- If asked about unrelated topics, politely refuse.

GREETING RULE:
- If user says "hello" or "hi" -> Reply in English: "Hello! I am EthioChain AI. How can I help you with your supply chain today?"
- If user says "ሰላም" -> Reply in Amharic: "ሰላም! እኔ EthioChain AI ነኝ። ለ ሰንሰለት አቅርቦት እንዴት ልርዳት?"
"""
    # ------------------------------------

    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in st.session_state.chat_history[-6:]:
        if "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + api_key.strip(),
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",  # Upgraded to 70B for better instruction following
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.2  # Lowered temperature for stricter rule following
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
        return f"️ Error: {str(e)}"
