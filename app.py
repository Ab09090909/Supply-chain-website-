import streamlit as st
from utils.auth import login

# Global page config
st.set_page_config(
    page_title="EthioChain",
    page_icon="🇪🇹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for branding
st.markdown("""
    <style>
    .stApp { background-color: #0f1117; }
    h1, h2, h3 { color: #2E86C1; }
    </style>
""", unsafe_allow_html=True)

st.title("🇪🇹 EthioChain")
st.markdown("### Ethiopia's Premier Commercial Supply Chain Platform")
st.markdown("Connecting producers, merchants, and customers across all sectors — Agriculture, Manufacturing, Construction, Textiles, and more.")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Routing logic
if not st.session_state.authenticated:
    st.markdown("---")
    st.subheader("🔐 Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if login(email, password):
                role = st.session_state.role
                # Route to the correct role page
                if role == "producer":
                    st.switch_page("pages/1_producer.py")
                elif role == "merchant":
                    st.switch_page("pages/2_merchant.py")
                elif role == "customer":
                    st.switch_page("pages/3_customer.py")
                elif role == "admin":
                    st.switch_page("pages/4_admin.py")
                else:
                    st.error("Unknown role. Please contact support.")
else:
    # If already authenticated, redirect to their dashboard
    role = st.session_state.role
    if role == "producer":
        st.switch_page("pages/1_producer.py")
    elif role == "merchant":
        st.switch_page("pages/2_merchant.py")
    elif role == "customer":
        st.switch_page("pages/3_customer.py")
    elif role == "admin":
        st.switch_page("pages/4_admin.py")
