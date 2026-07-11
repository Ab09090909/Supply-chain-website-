import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.db import supabase
from utils.constants import format_etb

def render_admin_dashboard():
    if st.session_state.get("role") != "admin":
        st.switch_page("app.py")
        
    st.title("📊 Platform Overview")
    st.markdown("Welcome to the EthioChain Admin Dashboard.")
    
    try:
        # Fetch metrics
        users_res = supabase.table("profiles").select("role").execute()
        users = users_res.data if users_res.data else []
        
        products_res = supabase.table("products").select("id, status").execute()
        products = products_res.data if products_res.data else []
        
        orders_res = supabase.table("orders").select("total_price_etb, status, created_at").execute()
        orders = orders_res.data if orders_res.data else []
        
        fraud_res = supabase.table("fraud_logs").select("id, created_at").execute()
        fraud_logs = fraud_res.data if fraud_res.data else []
        
        # Calculate metrics
        total_users = len(users)
        total_products = len([p for p in products if p["status"] == "active"])
        total_transactions = len(orders)
        total_revenue = sum(o["total_price_etb"] for o in orders if o["status"] in ["Delivered", "Completed"])
        
        # Fraud alerts today
        today_str = pd.Timestamp.now().strftime('%Y-%m-%d')
        fraud_today = len([f for f in fraud_logs if f["created_at"][:10] == today_str])
        
        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("👥 Total Users", total_users)
        col2.metric("📦 Active Products", total_products)
        col3.metric("🛒 Total Transactions", total_transactions)
        col4.metric("💰 Total Revenue", format_etb(total_revenue))
        col5.metric("🚨 Fraud Alerts Today", fraud_today)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Users by Role")
            if users:
                df_users = pd.DataFrame(users)
                role_counts = df_users['role'].value_counts().reset_index()
                role_counts.columns = ['role', 'count']
                fig1 = px.pie(role_counts, values='count', names='role', title='User Distribution by Role', hole=0.4)
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("No user data available.")
                
        with col2:
            st.subheader("📈 Transaction Trends")
            if orders:
                df_orders = pd.DataFrame(orders)
                df_orders['created_at'] = pd.to_datetime(df_orders['created_at']).dt.date
                daily_revenue = df_orders.groupby('created_at')['total_price_etb'].sum().reset_index()
                
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=daily_revenue['created_at'],
                    y=daily_revenue['total_price_etb'],
                    mode='lines+markers',
                    name='Daily Revenue (ETB)',
                    line=dict(color='#2E86C1', width=3)
                ))
                fig2.update_layout(
                    title="Daily Platform Revenue",
                    xaxis_title="Date",
                    yaxis_title="Revenue (ETB)",
                    template="plotly_dark"
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No order data available.")
                
    except Exception as e:
        st.error(f"Failed to load dashboard metrics: {str(e)}")
