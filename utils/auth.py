import streamlit as st
from utils.db import supabase

def login(email: str, password: str) -> bool:
    """Handles user login via Supabase Auth and sets session state."""
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = res.user
        
        if not user:
            st.error("Invalid email or password.")
            return False

        profile_res = supabase.table("profiles").select("*").eq("id", user.id).execute()
        
        if not profile_res.data:
            st.error("User profile not found. Please contact an administrator.")
            return False

        profile = profile_res.data[0]

        st.session_state.user_id = user.id
        st.session_state.role = profile["role"]
        st.session_state.name = profile["name"]
        st.session_state.city = profile["city"]
        st.session_state.authenticated = True

        return True

    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False

def signup(email: str, password: str, name: str, city: str, role: str, phone: str = None) -> bool:
    """Handles user signup via Supabase Auth and creates a profile."""
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "name": name,
                    "city": city,
                    "role": role,
                    "phone": phone
                }
            }
        })
        
        user = res.user
        if not user:
            st.error("Signup failed. Please try again.")
            return False
            
        profile_data = {
            "id": user.id,
            "role": role,
            "name": name,
            "city": city,
            "phone": phone,
            "verification_status": "unverified"
        }
        
        try:
            supabase.table("profiles").insert(profile_data).execute()
        except Exception:
            supabase.table("profiles").update(profile_data).eq("id", user.id).execute()
            
        st.success("Account created successfully! Please log in.")
        return True
        
    except Exception as e:
        if "already registered" in str(e).lower() or "duplicate" in str(e).lower():
            st.error("This email is already registered. Please log in.")
        else:
            st.error(f"Signup failed: {str(e)}")
        return False

def reset_password(email: str) -> bool:
    """Sends a password reset email via Supabase Auth."""
    try:
        # Supabase will send a magic link/password reset link to the user's email
        supabase.auth.reset_password_for_email(email)
        return True
    except Exception as e:
        st.error(f"Failed to send reset email: {str(e)}")
        return False

def logout():
    """Clears session state and logs the user out."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    
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
