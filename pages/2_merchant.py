import streamlit as st
from utils.nav import render_sidebar
from utils.chatbot import render_chatbot_tab
from merchant.dashboard import render_merchant_dashboard
from merchant.marketplace import render_marketplace
from merchant.producer_matching import render_producer_matching
from merchant.fraud_check import render_fraud_check

st.set_page_config(page_title="Merchant Dashboard", page_icon="🏪", layout="wide")

if st.session_state.get("role") != "merchant":
    st.switch_page("app.py")

render_sidebar()

tab = st.session_state.get("current_tab", "Dashboard")
if tab == "Dashboard":
    render_merchant_dashboard()
elif tab == "Marketplace":
    render_marketplace()
elif tab == "Find Producers":
    render_producer_matching()
elif tab == "Fraud Check":
    render_fraud_check()
elif tab == "AI Assistant":
    render_chatbot_tab()
