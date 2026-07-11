import streamlit as st
import requests

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
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_response(prompt, role)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

def get_response(prompt, role):
    """Calls Groq API to get AI response."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "⚠️ GROQ_API_KEY not found in secrets."
    
    messages = [
        {"role": "system", "content": f"You are EthioChain AI, an assistant for an Ethiopian agricultural supply chain platform. The user role is: {role}. Always quote prices in ETB."},
    ]
    messages += st.session_state.chat_history[-200:]  # Keep last 10 messages
    messages.append({"role": "user", "content": prompt})
    
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + api_key.strip(),
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if resp.status_code != 200:
            return f"⚠️ API Error {resp.status_code}: {resp.text}"
            
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return "Error: " + str(e)
