def _get_groq_response(prompt: str, role: str) -> str:
    api_key = st.secrets.get("GROQ_API_KEY")
    
    if not api_key:
        return "⚠️ Groq API Key not found in secrets. Please check your Streamlit Cloud configuration."
    
    # Clean the API key (remove any whitespace or quotes)
    api_key = str(api_key).strip().strip('"').strip("'")
    
    if not api_key.startswith("gsk_"):
        return f"⚠️ Invalid Groq API key format. Key should start with 'gsk_' but got: {api_key[:10]}..."
    
    system_prompt = get_system_prompt(role)
    
    # Build messages array correctly
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    # Add history if exists (last 5 messages to avoid token limits)
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history[-5:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    try:
        import json
        # Prepare the request payload
        payload = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        response = requests.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        
        # Check for specific HTTP errors
        if response.status_code == 401:
            return "️ **401 Unauthorized** - Invalid API key. Please check your GROQ_API_KEY in Streamlit secrets."
        elif response.status_code == 400:
            error_detail = response.json().get("error", {}).get("message", "Unknown error")
            return f"⚠️ **400 Bad Request** - {error_detail}"
        elif response.status_code == 429:
            return "⚠️ **429 Rate Limit** - Too many requests. Please wait a moment and try again."
        elif response.status_code >= 500:
            return "⚠️ **Server Error** - Groq service is temporarily unavailable. Please try again later."
        
        response.raise_for_status()
        result = response.json()
        
        if "choices" not in result or len(result["choices"]) == 0:
            return "⚠️ Unexpected response format from Groq API."
            
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.Timeout:
        return "⚠️ **Timeout** - The request took too long. Please try again."
    except requests.exceptions.ConnectionError:
        return "⚠️ **Connection Error** - Cannot reach Groq API. Check your internet connection."
    except Exception as e:
        return f"⚠️ **Error**: {type(e).__name__} - {str(e)}"
