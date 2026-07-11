import streamlit as st
from utils.db import supabase

def render_system_settings():
    if st.session_state.get("role") != "admin":
        st.switch_page("app.py")
        
    st.title("⚙️ System Settings")
    
    # Supabase Connection Status
    st.subheader("🔌 Database Connection")
    try:
        res = supabase.table("profiles").select("id").limit(1).execute()
        st.success("✅ Supabase connection is healthy.")
    except Exception as e:
        st.error(f"❌ Supabase connection failed: {str(e)}")
        
    # API Keys Health Check
    st.subheader("🔑 API Keys & Secrets")
    secrets_status = {
        "SUPABASE_URL": "SUPABASE_URL" in st.secrets,
        "SUPABASE_KEY": "SUPABASE_KEY" in st.secrets,
        "OPENROUTER_API_KEY": "OPENROUTER_API_KEY" in st.secrets
    }
    
    for key, status in secrets_status.items():
        if status:
            st.success(f"✅ {key} is configured.")
        else:
            st.error(f"❌ {key} is missing.")
            
    # Feature Toggles
    st.subheader("🎛️ Feature Toggles")
    col1, col2 = st.columns(2)
    
    with col1:
        enable_chatbot = st.toggle("Enable AI Chatbot", value=True)
        enable_fraud_check = st.toggle("Enable Fraud Detection", value=True)
        
    with col2:
        enable_recommendations = st.toggle("Enable Product Recommendations", value=True)
        enable_demand_forecast = st.toggle("Enable Demand Forecasting", value=True)
        
    if st.button("Save Settings", use_container_width=True):
        st.session_state["feature_chatbot"] = enable_chatbot
        st.session_state["feature_fraud"] = enable_fraud_check
        st.session_state["feature_recommendations"] = enable_recommendations
        st.session_state["feature_demand"] = enable_demand_forecast
        st.success("Settings saved successfully!")
        
    # Environment Info
    st.subheader("🌍 Environment Info")
    st.info(f"**Deployment Environment:** Streamlit Community Cloud")
    st.info(f"**Python Version:** 3.10+")
    st.info(f"**Current Date:** July 11, 2026")
