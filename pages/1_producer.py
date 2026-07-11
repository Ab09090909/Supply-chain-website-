import streamlit as st
from utils.nav import render_sidebar
from utils.chatbot import render_chatbot
from producer.dashboard import render_producer_dashboard

st.set_page_config(page_title="Producer Dashboard", page_icon="🏭", layout="wide")

if st.session_state.get("role") != "producer":
    st.switch_page("app.py")

render_sidebar()
render_producer_dashboard()
render_chatbot()
