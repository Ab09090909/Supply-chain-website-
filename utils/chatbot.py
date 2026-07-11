import streamlit as st
import requests
from utils.ai_instructions import get_system_prompt

def render_chatbot():
    """Renders the AI chatbot as a floating panel."""
    # Inject CSS for floating effect
    st.markdown("""
    <style>
    .floating-chatbot {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        background-color: #1a1d29;
        border: 1px solid #2E86C1;
        border-radius: 12px;
        padding: 15px;
        width: 320px;
        max-height: 450px;
        overflow-y: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .floating-chatbot .stChatMessage {
        background-color: transparent !important;
        padding: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="floating-chatbot">', unsafe_allow_html=True)
        
        st.subheader("💬 EthioChain AI")
        st.caption("English / አማርኛ")
        
        role = st.session_state.get("role", "customer")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if prompt := st.chat_input("Ask me...", key="chatbot_input"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = _get_openrouter_response(prompt, role)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
        st.markdown('</div>', unsafe_allow_html=True)

def _get_openrouter_response(prompt: str, role: str) -> str:
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if not api_key:
        return "⚠️ AI Assistant is currently unavailable."
        
    system_prompt = get_system_prompt(role)
    messages = [{"role": "system", "content": system_prompt}]
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
        return f"⚠️ Error: {str(e)}"
