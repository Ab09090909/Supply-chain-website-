import streamlit as st
from utils.nav import render_sidebar
from utils.chatbot import render_chatbot
from admin.dashboard import render_admin_dashboard
from admin.user_management import render_user_management
from admin.product_management import render_product_management
from admin.fraud_monitoring import render_fraud_monitoring
from admin.ml_performance import render_ml_performance
from admin.system_settings import render_system_settings
from admin.reports import render_reports

st.set_page_config(page_title="Admin Dashboard", page_icon="🛡️", layout="wide")

if st.session_state.get("role") != "admin":
    st.error(" Access Denied. Admin privileges required.")
    st.switch_page("app.py")

render_sidebar()

tab = st.session_state.get("current_tab", "Dashboard")
if tab == "Dashboard":
    render_admin_dashboard()
elif tab == "Users":
    render_user_management()
elif tab == "Products":
    render_product_management()
elif tab == "Fraud Alerts":
    render_fraud_monitoring()
elif tab == "AI Models":
    render_ml_performance()
elif tab == "Settings":
    render_system_settings()
elif tab == "Reports":
    render_reports()

render_chatbot()
