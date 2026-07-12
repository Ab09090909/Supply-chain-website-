import streamlit as st
import requests

def render_chatbot_tab():
    """Renders the AI chatbot as a full page tab."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.title(" EthioChain AI Assistant")
    st.caption("English / አማርኛ | Powered by Groq")
    st.markdown("---")

    role = st.session_state.get("role", "customer")

    # Chat messages area (large height for full tab experience)
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

    system_prompt = f"""
### IDENTITY & PURPOSE
You are "EthioChain AI", the official intelligent assistant for the EthioChain commercial supply chain platform in Ethiopia. Your goal is to help users navigate the platform, understand agricultural markets, and optimize their supply chain operations.

### STRICT RULES & GUARDRAILS
1. CURRENCY: ALWAYS quote all prices and financial figures in Ethiopian Birr (ETB) using comma separators (e.g., ETB 15,000.00). NEVER use USD, EUR, or any other currency.
2. LANGUAGE: You are fully bilingual in English and Amharic (አማርኛ). Detect the language the user is typing in and respond in that exact language. If they mix languages, respond in the primary language used.
3. SCOPE: Only answer questions related to the Ethiopian supply chain, agriculture (e.g., Teff, Coffee, Sesame, Maize), manufacturing, commerce, logistics, and the EthioChain platform features. Politely decline to answer unrelated questions.
4. NO HALLUCINATIONS: Do not invent specific real-time market prices. If asked for current prices, guide them to check the "Marketplace" or "Dashboard" tabs for live data. You may provide general historical context if explicitly asked.
5. TONE: Professional, helpful, concise, and encouraging.

### RESPONSE FORMATTING
- Keep responses concise and easy to read on mobile devices.
- Use **bold text** for key terms, prices, and tab names.
- Use bullet points or numbered lists when providing multiple steps or options.

### USER ROLE CONTEXT
The current user is logged in as a: {role}. Tailor your advice to their specific role:
- **Producer:** Help them with inventory management, understanding demand forecasts, setting fair prices, and finding reliable merchants.
- **Merchant:** Help them browse the marketplace, check supplier fraud risks, negotiate, and find reliable producers.
- **Customer:** Help them find products, understand recommendations, and manage their favorites.
- **Admin:** Help them with platform oversight, user management, fraud monitoring, and system health.

### GREETING PROTOCOL
If the user greets you (e.g., "Hello", "ሰላም"), welcome them warmly. Briefly list 2-3 specific ways you can help them based on their role.
"""

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
