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
    """Renders the chat window using native Streamlit components."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chatbot_visible:
        return

    role = st.session_state.get("role", "customer")

    # Chat window styling
    st.markdown("""
    <style>
    .chat-container {
        background: linear-gradient(135deg, #1a1d29 0%, #0f1117 100%);
        border: 2px solid #2E86C1;
        border-radius: 16px;
        padding: 0;
        overflow: hidden;
        margin-top: 10px;
    }
    .chat-header-bar {
        background: linear-gradient(135deg, #2E86C1 0%, #1a5276 100%);
        padding: 14px 20px;
        border-radius: 12px 12px 0 0;
    }
    .chat-title {
        color: white;
        font-size: 18px;
        font-weight: bold;
        margin: 0;
    }
    .chat-subtitle {
        color: #d0e8f5;
        font-size: 12px;
        margin: 3px 0 0 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header with close button
    st.markdown("""
    <div class="chat-header-bar">
        <p class="chat-title">💬 EthioChain AI</p>
        <p class="chat-subtitle">English / አማርኛ</p>
    </div>
    """, unsafe_allow_html=True)

    # Close button (native Streamlit — always works)
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("✖ Close", key="close_chat_btn", type="secondary"):
            st.session_state.chatbot_visible = False
            st.session_state.chat_history = []
            st.rerun()

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Native chat input — this is what actually works in Streamlit
    prompt = st.chat_input("Ask me anything...", key="chat_input_field")

    if prompt:
        # Show user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Get and show assistant response
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

    # Add last 8 messages for context
    for msg in st.session_state.chat_history[-8:]:
        if "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Merge consecutive same-role messages to satisfy Groq's alternating requirement
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
                "model": "llama-3.1-8b-instant",
                "messages": cleaned_messages,
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )

        if resp.status_code != 200:
            try:
                error_msg = resp.json().get("error", {}).get("message", resp.text)
            except Exception:
                error_msg = resp.text
            return f"⚠️ API Error {resp.status_code}: {error_msg}"

        return resp.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "⚠️ Request timeout. Please try again."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
