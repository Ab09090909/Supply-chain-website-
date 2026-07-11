import streamlit as st
from utils.nav import render_sidebar
from utils.chatbot import render_chatbot
from producer.dashboard import render_producer_dashboard
from producer.inventory import render_inventory
from producer.merchant_matching import render_merchant_matching

st.set_page_config(page_title="Producer Dashboard", page_icon="🏭", layout="wide")

if st.session_state.get("role") != "producer":
    st.switch_page("app.py")

render_sidebar()

# AI Assistant button/chat at the top
render_chatbot()

tab = st.session_state.get("current_tab", "Dashboard")
if tab == "Dashboard":
    render_producer_dashboard()
elif tab == "Inventory":
    render_inventory()
elif tab == "Find Merchants":
    render_merchant_matching()
