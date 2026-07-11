import streamlit as st
from utils.db import supabase

def login(email: str, password: str) -> bool:
    """Handles user login via Supabase Auth and sets session state."""
    try:
        # Authenticate with Supabase
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = res.user
        
        if not user:
            st.error("Invalid email or password.")
            return False

        # Fetch user profile to get role and details
        profile_res = supabase.table("profiles").select("*").eq("id", user.id).execute()
        
        if not profile_res.data:
            st.error("User profile not found. Please contact an administrator.")
            return False

        profile = profile_res.data[0]

        # Store in session state
        st.session_state.user_id = user.id
        st.session_state.role = profile["role"]
        st.session_state.name = profile["name"]
        st.session_state.city = profile["city"]
        st.session_state.authenticated = True

        return True

    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False

def logout():
    """Clears session state and logs the user out."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    
    # Clear all session state keys
    for key in list(st.session_state.keys()):
        del st.session_state[key]
        
    st.switch_page("app.py")

def check_auth(required_role: str = None):
    """Checks if the user is authenticated and has the correct role."""
    if not st.session_state.get("authenticated"):
        st.switch_page("app.py")
    
    if required_role and st.session_state.get("role") != required_role:
        st.error(f"Access Denied. This page is for {required_role}s only.")
        st.switch_page("app.py")
