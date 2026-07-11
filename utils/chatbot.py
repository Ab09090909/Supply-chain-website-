import streamlit as st
import requests

def render_chatbot_button():
    """Renders the Open Chat button at the top of the page."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    
    if not st.session_state.chatbot_visible:
        if st.button("💬 Open Chat", key="top_chat_button", type="primary"):
            st.session_state.chatbot_visible = True
            st.rerun()

def render_chatbot_window():
    """Renders the floating chat window with working close button."""
    if "chatbot_visible" not in st.session_state:
        st.session_state.chatbot_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chatbot_visible:
        return

    role = st.session_state.get("role", "customer")
    
    # Handle closing the chat
    if st.session_state.get("close_chat_clicked"):
        st.session_state.chatbot_visible = False
        st.session_state.close_chat_clicked = False
        st.rerun()
    
    # Handle new message
    if st.session_state.get("new_chat_message"):
        prompt = st.session_state.new_chat_message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Get response
        response = get_response(prompt, role)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Clear the message
        st.session_state.new_chat_message = None
        st.rerun()

    # Build chat messages HTML
    messages_html = ""
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            messages_html += f"""
            <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
                <div style="background: #2E86C1; color: white; padding: 10px 15px; border-radius: 18px 18px 4px 18px; max-width: 80%; word-wrap: break-word;">
                    {message["content"]}
                </div>
            </div>
            """
        else:
            messages_html += f"""
            <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
                <div style="background: #2a2d36; color: #e8eaed; padding: 10px 15px; border-radius: 18px 18px 18px 4px; max-width: 80%; word-wrap: break-word;">
                    {message["content"]}
                </div>
            </div>
            """

    # Render floating chat window
    st.markdown(f"""
    <style>
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateY(-20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .chat-window {{
        position: fixed;
        top: 80px;
        right: 20px;
        width: 400px;
        max-width: 90vw;
        max-height: 70vh;
        background: linear-gradient(135deg, #1a1d29 0%, #0f1117 100%);
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.7);
        border: 2px solid #2E86C1;
        z-index: 9999;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        animation: slideIn 0.3s ease-out;
    }}
    .chat-header {{
        background: linear-gradient(135deg, #2E86C1 0%, #1a5276 100%);
        color: white;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #3a3d46;
    }}
    .chat-title {{
        font-size: 18px;
        font-weight: bold;
    }}
    .chat-subtitle {{
        font-size: 12px;
        color: #d0e8f5;
        margin-top: 3px;
    }}
    .close-btn {{
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }}
    .close-btn:hover {{
        background: rgba(255,0,0,0.7);
        transform: scale(1.1);
    }}
    .chat-messages {{
        background: #0f1117;
        padding: 15px;
        height: 350px;
        overflow-y: auto;
        flex-grow: 1;
    }}
    .chat-messages::-webkit-scrollbar {{
        width: 6px;
    }}
    .chat-messages::-webkit-scrollbar-track {{
        background: #1a1d29;
        border-radius: 10px;
    }}
    .chat-messages::-webkit-scrollbar-thumb {{
        background: #2E86C1;
        border-radius: 10px;
    }}
    .chat-input-area {{
        padding: 15px;
        background: #1a1d29;
        border-top: 1px solid #2E86C1;
    }}
    .chat-input {{
        width: 100%;
        padding: 12px 15px;
        border: 1px solid #2E86C1;
        border-radius: 25px;
        background: #0f1117;
        color: #e8eaed;
        font-size: 14px;
        outline: none;
    }}
    .chat-input:focus {{
        border-color: #5dade2;
        box-shadow: 0 0 10px rgba(46, 134, 193, 0.3);
    }}
    .send-btn {{
        background: #2E86C1;
        border: none;
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        cursor: pointer;
        font-weight: 600;
        margin-left: 10px;
        transition: all 0.2s;
    }}
    .send-btn:hover {{
        background: #5dade2;
        transform: translateY(-2px);
    }}
    </style>
    
    <div class="chat-window">
        <div class="chat-header">
            <div>
                <div class="chat-title">💬 EthioChain AI</div>
                <div class="chat-subtitle">English / አማርኛ</div>
            </div>
            <button class="close-btn" onclick="document.getElementById('close_chat_btn').click()" title="Close chat"></button>
        </div>
        <div class="chat-messages">
            {messages_html if messages_html else '<div style="text-align: center; color: #666; padding: 20px;">Start a conversation...</div>'}
        </div>
        <div class="chat-input-area">
            <div style="display: flex; gap: 10px;">
                <input type="text" class="chat-input" id="chat_input" placeholder="Ask me..." onkeypress="if(event.key === 'Enter') document.getElementById('send_btn').click()">
                <button class="send-btn" id="send_btn" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>
    
    <!-- Hidden Streamlit buttons for actions -->
    <button id="close_chat_btn" style="display:none;"></button>
    """, unsafe_allow_html=True)
    
    # Close button handler
    if st.button("", key="close_chat_btn"):
        st.session_state.close_chat_clicked = True
        st.rerun()
    
    # Send message via JavaScript
    st.markdown("""
    <script>
    function sendMessage() {
        var input = document.getElementById('chat_input');
        var message = input.value.trim();
        if (message) {
            // Store message in a way Streamlit can detect
            var event = new CustomEvent('chatMessage', {detail: message});
            document.dispatchEvent(event);
            input.value = '';
        }
    }
    
    // Listen for chat messages
    document.addEventListener('chatMessage', function(e) {
        // This will trigger a Streamlit rerun with the message
        var input = document.createElement('input');
        input.type = 'hidden';
        input.id = 'chat_message_input';
        input.value = e.detail;
        document.body.appendChild(input);
        
        // Click a hidden button to trigger rerun
        var btn = document.createElement('button');
        btn.id = 'message_submit_btn';
        btn.style.display = 'none';
        document.body.appendChild(btn);
        btn.click();
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Hidden button to trigger message send
    if 'message_submit_btn' in st.session_state or st.button("", key="message_submit_btn", type="secondary"):
        # Get message from JavaScript
        st.session_state.new_chat_message = st.session_state.get("js_chat_message", "")

def get_response(prompt, role):
    """Calls Groq API with detailed system instructions."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        return "️ GROQ_API_KEY not found in secrets."
    
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
