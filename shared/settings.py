import streamlit as st
from utils.db import supabase
from utils.constants import ETHIOPIAN_CITIES

def render_settings():
    """
    Renders user profile settings and allows updates.
    """
    st.subheader("⚙️ Profile Settings")
    
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Please log in to update settings.")
        return
        
    try:
        res = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if not res.data:
            st.error("Profile not found.")
            return
            
        profile = res.data[0]
        
        with st.form("settings_form"):
            name = st.text_input("Full Name", value=profile.get("name", ""))
            city = st.selectbox("City", ETHIOPIAN_CITIES, index=ETHIOPIAN_CITIES.index(profile.get("city", "Addis Ababa")) if profile.get("city") in ETHIOPIAN_CITIES else 0)
            phone = st.text_input("Phone Number", value=profile.get("phone", ""))
            
            submitted = st.form_submit_button("Save Changes")
            
            if submitted:
                try:
                    supabase.table("profiles").update({
                        "name": name,
                        "city": city,
                        "phone": phone
                    }).eq("id", user_id).execute()
                    
                    # Update session state
                    st.session_state.name = name
                    st.session_state.city = city
                    
                    st.success("Profile updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update profile: {str(e)}")
                    
    except Exception as e:
        st.error(f"Failed to load profile: {str(e)}")
