import streamlit as st
import pandas as pd
from utils.db import supabase

def render_fraud_monitoring():
    if st.session_state.get("role") != "admin":
        st.switch_page("app.py")
        
    st.title("🛡️ Fraud Monitoring")
    
    try:
        res = supabase.table("fraud_logs").select("*").order("created_at", desc=True).execute()
        logs = res.data
        
        if not logs:
            st.info("No fraud alerts recorded yet.")
            return
            
        df = pd.DataFrame(logs)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            reviewed_filter = st.selectbox("Review Status", ["All", "Unreviewed", "Reviewed"])
        with col2:
            risk_filter = st.selectbox("Risk Level", ["All", "High (>0.7)", "Medium (0.3-0.7)", "Low (<0.3)"])
        with col3:
            date_filter = st.date_input("Filter by Date", value=None)
            
        if reviewed_filter != "All":
            df = df[df["reviewed"] == (reviewed_filter == "Reviewed")]
            
        if risk_filter != "All":
            if "High" in risk_filter:
                df = df[df["risk_score"] > 0.7]
            elif "Medium" in risk_filter:
                df = df[(df["risk_score"] >= 0.3) & (df["risk_score"] <= 0.7)]
            elif "Low" in risk_filter:
                df = df[df["risk_score"] < 0.3]
                
        if date_filter:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.date
            df = df[df['created_at'] == date_filter]
            
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("⚙️ Alert Actions")
        
        if not df.empty:
            log_ids = df["id"].tolist()
            selected_log = st.selectbox("Select Alert to Manage", log_ids)
            
            if selected_log:
                col1, col2, col3 = st.columns(3)
                
                if col1.button("✅ Mark as Reviewed", use_container_width=True):
                    supabase.table("fraud_logs").update({"reviewed": True}).eq("id", selected_log).execute()
                    st.success("Alert marked as reviewed!")
                    st.rerun()
                    
                if col2.button("🚫 Block Related User", use_container_width=True):
                    st.info("User blocking logic would go here based on transaction details.")
                    
                if col3.button("🧹 Clear False Positive", use_container_width=True):
                    supabase.table("fraud_logs").delete().eq("id", selected_log).execute()
                    st.success("Alert cleared!")
                    st.rerun()
        else:
            st.info("No alerts match the current filters.")
                
    except Exception as e:
        st.error(f"Failed to load fraud logs: {str(e)}")
