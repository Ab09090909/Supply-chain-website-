import streamlit as st
from utils.nav import render_sidebar
from utils.chatbot import render_chatbot
from merchant.dashboard import render_merchant_dashboard

st.set_page_config(page_title="Merchant Dashboard", page_icon="🏪", layout="wide")

if st.session_state.get("role") != "merchant":
    st.switch_page("app.py")

render_sidebar()
render_merchant_dashboard()
render_chatbot()
