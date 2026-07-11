def get_response(prompt, role):
    """Calls Groq API to get AI response."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "⚠️ GROQ_API_KEY not found in secrets."
    
    # Build messages array properly - NO DUPLICATES
    messages = [
        {"role": "system", "content": f"You are EthioChain AI, an assistant for an Ethiopian agricultural supply chain platform. The user role is: {role}. Always quote prices in ETB."}
    ]
    
    # Add chat history (but NOT the current prompt - it's already in history)
    # Filter out any malformed messages
    for msg in st.session_state.chat_history[-10:]:
        if "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Ensure messages alternate properly (remove consecutive same-role messages)
    cleaned_messages = [messages[0]]  # Keep system prompt
    for i in range(1, len(messages)):
        if messages[i]["role"] != messages[i-1]["role"]:
            cleaned_messages.append(messages[i])
        else:
            # If same role, merge content
            cleaned_messages[-1]["content"] += "\n" + messages[i]["content"]
    
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + api_key.strip(),
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",  # Updated model name
                "messages": cleaned_messages,
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        
        # Show detailed error if request fails
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

def render_chatbot():
    """Renders the floating AI chatbot."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Show open button if closed
    if not st.session_state.chatbot_visible:
        if st.button("💬 Chat", key="fab_open_chat"):
            st.session_state.chatbot_visible = True
            st.rerun()
        return

    # Chat interface
    st.markdown("### 💬 EthioChain AI")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption("English / አማርኛ")
    with col2:
        if st.button("❌ Exit", key="chat_exit_btn"):
            st.session_state.chatbot_visible = False
            st.rerun()
            
    role = st.session_state.get("role", "customer")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Chat input
    if prompt := st.chat_input("Ask me...", key="chat_input_field"):
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
            
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_response(prompt, role)
                st.markdown(response)
                # Add assistant response to history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
