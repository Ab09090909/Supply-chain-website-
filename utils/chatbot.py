import streamlit as st
import requests


def render_chatbot_tab():
    """Renders the AI chatbot as a fixed-position tab."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

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
    .fixed-chat-header {
        background: #2E86C1 !important;
        color: white !important;
        padding: 10px 15px !important;
        flex-shrink: 0 !important;
    }
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
    .fixed-chat-input {
        padding: 10px !important;
        background: #1a1d29 !important;
        border-top: 1px solid #2E86C1 !important;
        flex-shrink: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="fixed-chat-container">', unsafe_allow_html=True)

    st.markdown("""
    <div class="fixed-chat-header">
        <div class="fixed-chat-title">💬 EthioChain AI</div>
        <div class="fixed-chat-subtitle">Powered by Groq</div>
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
        st.markdown(
            '<div style="text-align:center;color:#666;padding:10px;font-size:13px;">'
            '👋 Welcome! Ask me anything.</div>',
            unsafe_allow_html=True
        )

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-end;margin:5px 0;">
                <div style="background:#2E86C1;color:white;padding:8px 12px;
                            border-radius:14px 14px 2px 14px;max-width:90%;
                            word-wrap:break-word;font-size:13px;">
                    {message["content"]}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-start;margin:5px 0;">
                <div style="background:#2a2d36;color:#e8eaed;padding:8px 12px;
                            border-radius:14px 14px 14px 2px;max-width:90%;
                            word-wrap:break-word;font-size:13px;">
                    {message["content"]}
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="fixed-chat-input">', unsafe_allow_html=True)

    if prompt := st.chat_input("Type message...", key="fixed_chat_input"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.spinner(""):
            response = get_response(prompt, role)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)


def get_response(prompt, role):
    """Calls Groq API — English only."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "⚠️ GROQ_API_KEY not found in secrets."

    system_prompt = f"""You are EthioChain AI, the official assistant for the EthioChain supply chain platform in Ethiopia.

LANGUAGE: You ONLY respond in English. If the user writes in any other language, politely reply in English and ask them to write in English.

USER ROLE: {role}
Tailor advice to the role:
- Producer: inventory management, demand forecasts, pricing, finding merchants.
- Merchant: marketplace browsing, fraud risk checks, finding producers.
- Customer: product search, recommendations, favorites.
- Admin: platform oversight, user management, fraud monitoring.

CURRENCY: Always use ETB (e.g., ETB 1,500). Never use USD or any other currency.

SCOPE: Only discuss Ethiopian agriculture (Teff, Coffee, Sesame, Maize, etc.), supply chain, logistics, and EthioChain platform features. Politely decline unrelated questions.

ACCURACY: Never invent real-time prices. Direct users to the Marketplace or Dashboard tabs for live data.

TONE: Professional, helpful, concise. Format responses with bullet points or bold text for readability on mobile.

GREETING: If the user says hello or hi, respond: "Hello! I'm EthioChain AI. How can I help you with your supply chain today?"
"""

    messages = [{"role": "system", "content": system_prompt}]

    for msg in st.session_state.chat_history[-6:]:
        if "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Fix consecutive same-role messages
    cleaned_messages = [messages[0]]
    for i in range(1, len(messages)):
        if messages[i]["role"] != cleaned_messages[-1]["role"]:
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
                "model": "llama3-70b-8192",
                "messages": cleaned_messages,
                "max_tokens": 500,
                "temperature": 0.2
            },
            timeout=30
        )

        if resp.status_code != 200:
            try:
                error_data = resp.json()
                error_msg = error_data.get("error", {}).get("message", resp.text)
                return f"⚠️ API Error {resp.status_code}: {error_msg}"
            except Exception:
                return f"⚠️ API Error {resp.status_code}: {resp.text}"

        return resp.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "⚠️ Request timeout. Please try again."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
