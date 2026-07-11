import streamlit as st
from utils.nav import render_sidebar
from utils.chatbot import render_chatbot
from admin.dashboard import render_admin_dashboard

st.set_page_config(page_title="Admin Dashboard", page_icon="🛡️", layout="wide")

if st.session_state.get("role") != "admin":
    st.error("⛔ Access Denied. Admin privileges required.")
    st.switch_page("app.py")

render_sidebar()
render_admin_dashboard()
render_chatbot()
