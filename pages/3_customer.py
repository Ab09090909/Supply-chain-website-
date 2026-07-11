import streamlit as st
from utils.nav import render_sidebar
from utils.chatbot import render_chatbot
from customer.home import render_customer_home
from customer.marketplace import render_customer_marketplace
from customer.recommendations import render_recommendations
from customer.favorites import render_favorites

st.set_page_config(page_title="Customer Home", page_icon="🛍️", layout="wide")

if st.session_state.get("role") != "customer":
    st.switch_page("app.py")

render_sidebar()

tab = st.session_state.get("current_tab", "Home")
if tab == "Home":
    render_customer_home()
elif tab == "Marketplace":
    render_customer_marketplace()
elif tab == "For You":
    render_recommendations()
elif tab == "Favorites":
    render_favorites()

render_chatbot()
