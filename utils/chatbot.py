import streamlit as st
import requests


def render_chatbot():
    """Renders the EthioChain AI chatbot entirely in the sidebar."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    role = st.session_state.get("role", "customer")

    with st.sidebar:
        st.markdown("## 💬 EthioChain AI")
        st.caption("English / አማርኛ")
        st.divider()

        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        prompt = st.chat_input("Ask me anything...", key="sidebar_chat_input")

        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_response(prompt, role)
                st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

        # Clear chat button
        if st.session_state.chat_history:
            if st.button("🗑️ Clear Chat", key="clear_chat_btn", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()


def get_response(prompt, role):
    """Calls Groq API with system instructions."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "⚠️ GROQ_API_KEY not found in secrets."

    system_prompt = f"""You are EthioChain AI, the official intelligent assistant for the EthioChain commercial supply chain platform in Ethiopia.

STRICT RULES:
1. CURRENCY: ALWAYS quote all prices in Ethiopian Birr (ETB), e.g. ETB 15,000.00. NEVER use USD or EUR.
2. LANGUAGE: Fully bilingual in English and Amharic (አማርኛ). Respond in the same language the user writes in.
3. SCOPE: Only answer questions related to Ethiopian supply chain, agriculture, manufacturing, commerce, logistics, and EthioChain platform features. Politely decline unrelated questions.
4. TONE: Professional, helpful, concise, and encouraging.
5. NAVIGATION: Guide users to the correct page/tab when they ask how to do something on the platform.

USER ROLE: {role}
- Producer: Help with inventory, demand forecasts, finding merchants.
- Merchant: Help with marketplace browsing, fraud risk checks, finding producers.
- Customer: Help with finding products, recommendations, managing favorites.
- Admin: Help with platform oversight, user management, system health.

If the user greets you, welcome them warmly and list 2-3 ways you can help based on their role."""

    messages = [{"role": "system", "content": system_prompt}]

    # Add last 8 messages for context
    for msg in st.session_state.chat_history[-8:]:
        if "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Merge consecutive same-role messages (Groq requires alternating roles)
    cleaned = [messages[0]]
    for i in range(1, len(messages)):
        if messages[i]["role"] != cleaned[-1]["role"]:
            cleaned.append(messages[i])
        else:
            cleaned[-1]["content"] += "\n" + messages[i]["content"]

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + api_key.strip(),
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": cleaned,
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
