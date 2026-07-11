import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.db import supabase
from utils.constants import format_etb

def render_merchant_dashboard():
    if st.session_state.get("role") != "merchant":
        st.switch_page("app.py")
        
    st.title(f"👋 Welcome, {st.session_state.get('name', 'Merchant')}")
    st.markdown("Here is an overview of your purchasing activity and orders.")
    
    user_id = st.session_state.get("user_id")
    
    try:
        orders_res = supabase.table("orders").select("total_price_etb, status, created_at").eq("buyer_id", user_id).execute()
        orders = orders_res.data if orders_res.data else []
        
        total_purchases = len(orders)
        active_orders = len([o for o in orders if o["status"] in ["Pending", "Confirmed", "Shipped"]])
        money_spent = sum(o["total_price_etb"] for o in orders if o["status"] in ["Delivered", "Completed"])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🛒 Total Purchases", total_purchases)
        col2.metric("📦 Active Orders", active_orders)
        col3.metric("💰 Total Spent", format_etb(money_spent))
        
        st.markdown("---")
        st.subheader("📈 Purchase Trends")
        
        if orders:
            df = pd.DataFrame(orders)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.sort_values('created_at')
            df['cumulative_spent'] = df['total_price_etb'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['created_at'],
                y=df['cumulative_spent'],
                mode='lines+markers',
                name='Cumulative Spend (ETB)',
                line=dict(color='#27AE60', width=3)
            ))
            
            fig.update_layout(
                title="Cumulative Purchase Volume Over Time",
                xaxis_title="Date",
                yaxis_title="Total Spent (ETB)",
                template="plotly_dark",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No purchase history yet. Start exploring the marketplace!")
            
    except Exception as e:
        st.error(f"Failed to load dashboard metrics: {str(e)}")
