import streamlit as st
from utils.nav import render_sidebar
from utils.chatbot import render_chatbot
from customer.home import render_customer_home

st.set_page_config(page_title="Customer Home", page_icon="🛍️", layout="wide")

if st.session_state.get("role") != "customer":
    st.switch_page("app.py")

render_sidebar()
render_customer_home()
render_chatbot()
