import streamlit as st
import requests
from utils.ai_instructions import get_system_prompt

def render_chatbot():
    """
    Renders the AI chatbot UI at the bottom of the page.
    """
    st.markdown("---")
    st.subheader("💬 EthioChain AI Assistant")
    st.caption("Ask me anything about the supply chain... (English / አማርኛ)")
    
    role = st.session_state.get("role", "customer")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = _get_openrouter_response(prompt, role)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

def _get_openrouter_response(prompt: str, role: str) -> str:
    """Calls the OpenRouter API to get the AI response."""
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if not api_key:
        return "⚠️ AI Assistant is currently unavailable (API key missing in secrets)."
        
    system_prompt = get_system_prompt(role)
    
    # Build messages array
    messages = [{"role": "system", "content": system_prompt}]
    # Only keep the last 10 messages to avoid token limits
    messages.extend(st.session_state.chat_history[-10:])
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://ethiochain.streamlit.app",
                "X-Title": "EthioChain Assistant"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct:free", 
                "messages": messages
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Sorry, I encountered an error connecting to the AI service: {str(e)}"
