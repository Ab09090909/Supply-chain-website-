# pages/1_producer.py
import streamlit as st
from utils.chatbot import render_chatbot
from producer.dashboard import main as producer_dashboard_main

def main():
    # 1. Page Config
    st.set_page_config(
        page_title="Producer Dashboard - EthioChain",
        page_icon="🏭",
        layout="wide"
    )

    # 2. Verify Producer Role
    if "role" not in st.session_state or st.session_state.role != "producer":
        st.error("🚫 Access Denied: You must be logged in as a Producer to view this page.")
        if st.button("Go to Login"):
            st.switch_page("app.py")
        st.stop()

    # 3. Render Producer Dashboard
    producer_dashboard_main()

    # 4. Inject Floating Chatbot (Called here to avoid duplicates)
    render_chatbot()

if __name__ == "__main__":
    main()
