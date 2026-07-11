import streamlit as st
import requests

def render_chatbot():
    """Renders the floating AI chatbot with fixed position."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # CSS for fixed floating button and chat interface
    st.markdown("""
    <style>
    .floating-button-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
    }
    
    .chat-popup-card {
        position: fixed;
        bottom: 80px;
        right: 20px;
        z-index: 9999;
        width: 350px;
        max-width: 90vw;
        max-height: 60vh;
        background-color: #0f1117;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.6);
        border: 1px solid #2a2d36;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .chat-header {
        background-color: #2E86C1;
        color: white;
        padding: 15px 20px;
        font-size: 18px;
        font-weight: bold;
        flex-shrink: 0;
    }
    
    .chat-subtitle {
        color: #a0a0a0;
        font-size: 12px;
        margin-top: 5px;
    }
    
    .chat-history-container {
        background-color: #1a1d29;
        margin: 10px 15px;
        padding: 15px;
        height: 300px;
        overflow-y: auto;
        overflow-x: hidden;
        border-radius: 8px;
        border: 1px solid #2a2d36;
        flex-grow: 1;
    }
    
    .chat-history-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-history-container::-webkit-scrollbar-track {
        background: #1a1d29;
        border-radius: 10px;
    }
    
    .chat-history-container::-webkit-scrollbar-thumb {
        background: #2E86C1;
        border-radius: 10px;
    }
    
    .chat-input-container {
        margin: 0 15px 15px 15px;
        flex-shrink: 0;
    }
    
    .ai-assistant-btn {
        background: linear-gradient(135deg, #2E86C1 0%, #1a5276 100%);
        color: white;
        border: none;
        padding: 15px 25px;
        border-radius: 50px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(46, 134, 193, 0.4);
        display: flex;
        align-items: center;
        gap: 10px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .ai-assistant-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 134, 193, 0.6);
    }
    
    .exit-btn {
        float: right;
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
    }
    
    .exit-btn:hover {
        background: rgba(255,0,0,0.6);
    }
    </style>
    """, unsafe_allow_html=True)

    # If closed, show the floating "AI Assistant" button
    if not st.session_state.chatbot_visible:
        st.markdown("""
        <div class="floating-button-container">
            <button class="ai-assistant-btn" onclick="document.getElementById('chat-toggle').click()">
                <span>💬</span>
                <span>AI Assistant</span>
            </button>
        </div>
        """, unsafe_allow_html=True)
        
        # Hidden Streamlit button to trigger the state change
        if st.button("", key="chat-toggle", type="secondary"):
            st.session_state.chatbot_visible = True
            st.rerun()
        return

    # Chat interface is open
    st.markdown('<div class="chat-popup-card">', unsafe_allow_html=True)
    
    # Header with Exit button
    st.markdown("""
    <div class="chat-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span> EthioChain AI</span>
        </div>
        <div class="chat-subtitle">English / አማርኛ</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Exit button
    if st.button("❌ Exit", key="chat_exit_btn"):
        st.session_state.chatbot_visible = False
        st.rerun()
            
    role = st.session_state.get("role", "customer")
    
    # Chat history with independent scroll
    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)
            
    # Chat input
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Floating "AI Assistant" button (visible when chat is open too, for easy closing)
    st.markdown("""
    <div class="floating-button-container">
        <button class="ai-assistant-btn" onclick="document.getElementById('chat-toggle-close').click()">
            <span>💬</span>
            <span>AI Assistant</span>
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="chat-toggle-close", type="secondary"):
        st.session_state.chatbot_visible = False
        st.rerun()


def get_response(prompt, role):
    """Calls Groq API with detailed system instructions."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "️ GROQ_API_KEY not found in secrets."
    
    # Detailed system instructions for Groq
    system_prompt = f"""You are EthioChain AI, the official intelligent assistant for the EthioChain commercial supply chain platform in Ethiopia. 

STRICT RULES:
1. CURRENCY: ALWAYS quote all prices and financial figures in Ethiopian Birr (ETB) using comma separators (e.g., ETB 15,000.00). NEVER use USD, EUR, or any other currency.
2. LANGUAGE: You are fully bilingual in English and Amharic (አማርኛ). Detect the language the user is typing in and respond in that exact language.
3. SCOPE: Only answer questions related to the Ethiopian supply chain, agriculture, manufacturing, commerce, logistics, and the EthioChain platform features. Politely decline to answer unrelated questions.
4. TONE: Professional, helpful, concise, and encouraging.
5. PLATFORM NAVIGATION: If a user asks how to do something on the platform, guide them to the correct tab (e.g., "To add a product, please go to your Inventory tab").

USER ROLE CONTEXT:
The current user is logged in as a: {role}.
- If Producer: Help them with inventory management, understanding demand forecasts, and finding merchants.
- If Merchant: Help them browse the marketplace, check supplier fraud risks, and find reliable producers.
- If Customer: Help them find products, understand recommendations, and manage their favorites.
- If Admin: Help them with platform oversight, user management, and system health.

If the user greets you, welcome them warmly and briefly list 2-3 ways you can help them based on their role."""

    # Build messages array
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add chat history (limit to last 8 to save tokens)
    for msg in st.session_state.chat_history[-8:]:
        if "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Ensure messages alternate properly
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
