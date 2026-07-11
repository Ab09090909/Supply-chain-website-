import streamlit as st
import pandas as pd
from utils.db import supabase

def render_user_management():
    if st.session_state.get("role") != "admin":
        st.switch_page("app.py")
        
    st.title("👥 User Management")
    
    try:
        res = supabase.table("profiles").select("*").order("created_at", desc=True).execute()
        users = res.data
        
        if not users:
            st.info("No users found.")
            return
            
        df = pd.DataFrame(users)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            role_filter = st.multiselect("Filter by Role", ["producer", "merchant", "customer", "admin"], default=[])
        with col2:
            status_filter = st.multiselect("Filter by Status", ["verified", "unverified", "suspended"], default=[])
            
        if role_filter:
            df = df[df["role"].isin(role_filter)]
        if status_filter:
            df = df[df["verification_status"].isin(status_filter)]
            
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("⚙️ User Actions")
        
        user_ids = [u["id"] for u in users]
        selected_user = st.selectbox("Select User to Manage", user_ids, format_func=lambda x: f"{x} ({next((u['name'] for u in users if u['id'] == x), 'Unknown')})")
        
        if selected_user:
            col1, col2, col3 = st.columns(3)
            
            if col1.button("✅ Verify User", use_container_width=True):
                supabase.table("profiles").update({"verification_status": "verified"}).eq("id", selected_user).execute()
                st.success("User verified!")
                st.rerun()
                
            if col2.button("🚫 Suspend User", use_container_width=True):
                supabase.table("profiles").update({"verification_status": "suspended"}).eq("id", selected_user).execute()
                st.success("User suspended!")
                st.rerun()
                
            if col3.button("🗑️ Delete User", use_container_width=True):
                supabase.table("profiles").delete().eq("id", selected_user).execute()
                st.success("User deleted!")
                st.rerun()
                
    except Exception as e:
        st.error(f"Failed to load users: {str(e)}")
