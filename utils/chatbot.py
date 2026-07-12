import streamlit as st
import requests


def render_chatbot_tab():
    """Renders the AI chatbot as a full page tab."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.title("🤖 EthioChain AI Assistant")
    st.caption("English / አማርኛ | Powered by Groq")
    st.markdown("---")

    role = st.session_state.get("role", "customer")

    # Chat messages area
    chat_container = st.container(height=250, border=True)

    with chat_container:
        if not st.session_state.chat_history:
            st.info("👋 Welcome! Ask me anything about the EthioChain supply chain.")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Action buttons row
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    # Chat input
    if prompt := st.chat_input("Type your message...", key="tab_chat_input"):
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

### IDENTITY & PURPOSE
Your goal is to help users navigate the platform, understand agricultural markets, and optimize their supply chain operations.

### LANGUAGE RULES (STRICT — HIGHEST PRIORITY)
You are fully bilingual in English and Amharic (አማርኛ). Follow these rules exactly with zero exceptions:

DETECTION:
- User writes ONLY English → respond ENTIRELY in English. Do not include a single Amharic word or character.
- User writes ONLY Amharic → respond ENTIRELY in Amharic. Do not include a single English word except unavoidable platform-specific terms (EthioChain, Dashboard, Marketplace, Tab names).
- User mixes both languages → identify the dominant language and respond in that language. If equal, respond in Amharic.

AMHARIC QUALITY (when responding in Amharic):
- Write natural, fluent Ethiopian Amharic as educated Ethiopians write it — not word-for-word translations of English.
- Use correct Amharic grammar and sentence structure throughout.
- Never produce robotic or awkward phrasing from literal translation.
- Platform terms like "EthioChain", "Dashboard", "Marketplace" may remain in English even inside an Amharic response.

EXAMPLES (follow these exactly):
- User: "Hello" → full English response
- User: "ሰላም" → full Amharic response
- User: "How do I add products?" → full English response
- User: "ምርቶቼን እንዴት እጨምራለሁ?" → full Amharic response
- User: "Hello ሰላም" → Amharic response (Amharic detected)

CRITICAL: Never mix the two languages in one response. Pick one and use it exclusively.

### CURRENCY
ALWAYS quote all prices in Ethiopian Birr (ETB) with comma separators (e.g., ETB 15,000.00). NEVER use USD, EUR, or any other currency.

### SCOPE
Only answer questions related to: Ethiopian supply chain, agriculture (Teff, Coffee, Sesame, Maize, etc.), manufacturing, commerce, logistics, and EthioChain platform features. Politely decline unrelated questions.

### ACCURACY
Do not invent real-time market prices. If asked for current prices, direct the user to check the **Marketplace** or **Dashboard** tabs for live data. Historical context is allowed if explicitly requested.

### TONE
Professional, helpful, concise, and encouraging.

### RESPONSE FORMATTING
- Keep responses concise and easy to read on mobile.
- Use **bold text** for key terms, prices, and tab names.
- Use bullet points or numbered lists for multiple steps or options.

### USER ROLE CONTEXT
The current user is logged in as: **{role}**. Tailor your advice to their role:
- **Producer:** Inventory management, demand forecasts, fair pricing, finding reliable merchants.
- **Merchant:** Browsing the marketplace, checking supplier fraud risk, finding reliable producers.
- **Customer:** Finding products, understanding recommendations, managing favorites.
- **Admin:** Platform oversight, user management, fraud monitoring, system health.

### GREETING PROTOCOL
If the user greets you (e.g., "Hello", "ሰላም", "Hi"), welcome them warmly and briefly list 2–3 specific ways you can help them based on their role. Respond in the exact language they used to greet you.
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Add last 8 messages from history
    for msg in st.session_state.chat_history[-8:]:
        if "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Fix consecutive same-role messages (Groq requires alternating roles)
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
