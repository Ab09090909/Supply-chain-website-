# utils/chatbot.py
import streamlit as st
import requests
from utils.ai_instructions import get_system_prompt

def render_chatbot():
    """Renders the AI chatbot at the bottom of the page."""
    
    # Initialize chat history in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Use an expander at the bottom to simulate a collapsible panel
    with st.expander("💬 EthioChain AI Assistant", expanded=False):
        st.caption("Ask about supply chain, prices, forecasts, or fraud checks.")
        
        # Display existing chat messages
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input field
        if prompt := st.chat_input("Type your message here..."):
            # 1. Add user message to history and display it
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # 2. Get the correct system prompt for the current user role
            role = st.session_state.get("role", "customer")
            system_prompt = get_system_prompt(role)

            # 3. Prepare the messages payload for the API
            api_messages = [{"role": "system", "content": system_prompt}] + \
                           [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_messages]

            # 4. Call the OpenRouter API and display response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        api_key = st.secrets.get("OPENROUTER_API_KEY")
                        if not api_key:
                            st.error("️ OpenRouter API key is missing in Streamlit Secrets.")
                            return
                        
                        response = requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": "openrouter/auto", 
                                "messages": api_messages
                            },
                            timeout=30
                        )
                        response.raise_for_status()
                        data = response.json()
                        
                        ai_response = data["choices"][0]["message"]["content"]
                        st.markdown(ai_response)
                        
                        # Save assistant response to history
                        st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                        
                    except requests.exceptions.Timeout:
                        st.error(" The AI took too long to respond. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Failed to connect to AI: {str(e)}")
