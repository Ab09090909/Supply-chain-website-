import streamlit as st
from utils.auth import login, signup, reset_password
from utils.constants import ETHIOPIAN_CITIES

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
if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False

# Routing logic
if not st.session_state.authenticated:
    st.markdown("---")
    
    # If showing Forgot Password screen
    if st.session_state.show_forgot_password:
        st.subheader(" Reset Your Password")
        st.markdown("Enter your email address below. We will send you a link to reset your password.")
        
        with st.form("forgot_password_form"):
            email = st.text_input("Email Address")
            submitted = st.form_submit_button("Send Reset Link", use_container_width=True)
            
            if submitted:
                if reset_password(email):
                    st.success(f"✅ A password reset link has been sent to **{email}**. Please check your inbox (and spam folder).")
                    if st.button("⬅️ Back to Login", use_container_width=True):
                        st.session_state.show_forgot_password = False
                        st.rerun()
    else:
        # Toggle between Login and Sign Up
        auth_mode = st.radio("Choose an option", ["Login", "Sign Up"], horizontal=True)
        
        if auth_mode == "Login":
            st.subheader("🔐 Login to Your Account")
            with st.form("login_form"):
                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    if login(email, password):
                        role = st.session_state.role
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
                            
            # Forgot Password Button
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔑 Forgot Password?", use_container_width=True):
                st.session_state.show_forgot_password = True
                st.rerun()
                
        else:
            st.subheader("📝 Create a New Account")
            with st.form("signup_form"):
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                col1, col2 = st.columns(2)
                with col1:
                    role = st.selectbox("I am a...", ["customer", "producer", "merchant"])
                with col2:
                    city = st.selectbox("City", ETHIOPIAN_CITIES)
                    
                phone = st.text_input("Phone Number (Optional)")
                
                submitted = st.form_submit_button("Sign Up", use_container_width=True)
                
                if submitted:
                    if password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    else:
                        if signup(email, password, name, city, role, phone):
                            st.rerun() # Refresh to show the login form
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
