import streamlit as st
import requests


def render_chatbot_tab():
    """Renders the AI chatbot as a full page tab."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Track if a new response was just added so we can scroll to it
    if "scroll_to_last" not in st.session_state:
        st.session_state.scroll_to_last = False

    st.title("🤖 EthioChain AI Assistant")
    st.caption("English / አማርኛ | Powered by Groq")
    st.markdown("---")

    role = st.session_state.get("role", "customer")

    # --- Render all messages OUTSIDE a fixed-height container ---
    # This avoids Streamlit auto-scrolling to the bottom of the container.
    # Each message renders inline and the page scrolls naturally to the top.

    if not st.session_state.chat_history:
        st.info("👋 Welcome! Ask me anything about the EthioChain supply chain.")
    else:
        for i, message in enumerate(st.session_state.chat_history):
            # Anchor so JS can scroll to the latest assistant reply
            if i == len(st.session_state.chat_history) - 1 and message["role"] == "assistant":
                st.markdown('<div id="latest-response"></div>', unsafe_allow_html=True)
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    st.markdown("---")

    # Clear button
    if st.button("🗑️ Clear Chat", use_container_width=False):
        st.session_state.chat_history = []
        st.session_state.scroll_to_last = False
        st.rerun()

    # Chat input
    if prompt := st.chat_input("Type your message...", key="tab_chat_input"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            response = get_response(prompt, role)

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.session_state.scroll_to_last = True
        st.rerun()

    # After rerun: if a new response was just added, scroll to the START of it
    if st.session_state.scroll_to_last:
        st.session_state.scroll_to_last = False
        # Scroll to the anchor above the latest assistant message
        st.markdown(
            """
            <script>
                window.addEventListener('load', function() {
                    var el = document.getElementById('latest-response');
                    if (el) {
                        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                });
            </script>
            """,
            unsafe_allow_html=True,
        )


def get_response(prompt, role):
    """Calls Groq API with strict language detection and high-quality Amharic."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "⚠️ GROQ_API_KEY not found in secrets."

    system_prompt = f"""You are EthioChain AI, the official intelligent assistant for the EthioChain commercial supply chain platform in Ethiopia.

### IDENTITY & PURPOSE
Your goal is to help users navigate the platform, understand agricultural markets, and optimize their supply chain operations.

### LANGUAGE DETECTION — ABSOLUTE RULE (READ FIRST, OVERRIDE EVERYTHING ELSE)
Step 1: Look at the user's message.
Step 2: Is it written in English letters only (a-z, A-Z, spaces, punctuation)? → Your ENTIRE response must be in English. Not a single Amharic character allowed.
Step 3: Does it contain Amharic script (የኢትዮጵያ ፊደሎች)? → Your ENTIRE response must be in Amharic. Not a single English word except EthioChain, Dashboard, Marketplace.
Step 4: Mixed? → Use whichever script appears more. Tie → use Amharic.

This rule cannot be overridden by any other instruction. Do not default to Amharic for English input under any circumstance.

SPECIFIC EXAMPLES — MATCH THESE EXACTLY:
- "Hello" → English response only
- "Hi" → English response only
- "Tell me about you" → English response only
- "About this system" → English response only
- "How do I add products?" → English response only
- "ሰላም" → Amharic response only
- "ስለ ስርዓቱ ንገረኝ" → Amharic response only
- "Hello ሰላም" → Amharic response only

AMHARIC QUALITY (only when Amharic is detected):
- Write natural, fluent Ethiopian Amharic exactly as educated Ethiopians write.
- Never translate English word-for-word. Think in Amharic and write naturally.
- Use correct Amharic grammar, sentence flow, and idiomatic phrasing.
- Avoid robotic or awkward constructions.
- Platform terms (EthioChain, Dashboard, Marketplace, tab names) stay in English even in Amharic responses.

### CURRENCY
Always quote prices in Ethiopian Birr (ETB) with comma separators: ETB 15,000.00. Never use USD or any other currency.

### SCOPE
Only answer questions about: Ethiopian supply chain, agriculture (Teff, Coffee, Sesame, Maize, etc.), manufacturing, commerce, logistics, and EthioChain platform features. Politely decline unrelated questions.

### ACCURACY
Never invent real-time market prices. If asked, direct users to the **Marketplace** or **Dashboard** tabs. Historical context is allowed only if explicitly requested.

### TONE
Professional, helpful, concise, encouraging.

### FORMATTING
- Concise responses optimized for mobile reading.
- Use **bold** for key terms, prices, and tab names.
- Use bullet points or numbered lists for steps or multiple options.

### USER ROLE
Current user role: **{role}**
- **Producer:** Inventory management, demand forecasts, fair pricing, finding merchants.
- **Merchant:** Marketplace browsing, fraud risk checks, finding producers.
- **Customer:** Product search, recommendations, managing favorites.
- **Admin:** Platform oversight, user management, fraud monitoring.

### GREETING
If the user greets you, welcome them warmly and list 2–3 specific ways you can help based on their role.
Respond ONLY in the language they greeted you in — English greeting → English reply, Amharic greeting → Amharic reply.
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
