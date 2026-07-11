import streamlit as st
import requests
from utils.ai_instructions import get_system_prompt

def render_chatbot():
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # If chatbot is closed, show the open button
    if not st.session_state.chatbot_visible:
        if st.button("💬 Chat", key="fab_open_chat"):
            st.session_state.chatbot_visible = True
            st.rerun()
        return

    # If chatbot is open, show the interface
    st.markdown("###  EthioChain AI")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption("English / Amharic")
    with col2:
        if st.button("❌ Exit", key="chat_exit_btn"):
            st.session_state.chatbot_visible = False
            st.rerun()
            
    role = st.session_state.get("role", "customer")
    
    # Display history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Input
    if prompt := st.chat_input("Ask me...", key="chat_input_field"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = _get_groq_response(prompt, role)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

def _get_groq_response(prompt: str, role: str) -> str:
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "Groq API Key not configured in secrets."
    
    system_prompt = get_system_prompt(role)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = requests.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + str(api_key).strip(),
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": messages,
                "max_tokens": 500
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return "Error: " + str(e)
