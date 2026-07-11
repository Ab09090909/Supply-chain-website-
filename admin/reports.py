import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import supabase
from utils.constants import format_etb

def render_reports():
    if st.session_state.get("role") != "admin":
        st.switch_page("app.py")
        
    st.title("📊 Platform Reports")
    
    try:
        # Fetch data
        orders_res = supabase.table("orders").select("*, products(category, sector, city), profiles!orders_seller_id_fkey(name)").execute()
        orders = orders_res.data if orders_res.data else []
        
        if not orders:
            st.info("No order data available to generate reports.")
            return
            
        df = pd.DataFrame(orders)
        
        # Extract nested data
        df['category'] = df['products'].apply(lambda x: x.get('category', 'Unknown') if isinstance(x, dict) else 'Unknown')
        df['sector'] = df['products'].apply(lambda x: x.get('sector', 'Unknown') if isinstance(x, dict) else 'Unknown')
        df['city'] = df['products'].apply(lambda x: x.get('city', 'Unknown') if isinstance(x, dict) else 'Unknown')
        df['seller_name'] = df['profiles'].apply(lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else 'Unknown')
        
        # 1. Revenue by Sector
        st.subheader("💰 Revenue Breakdown by Sector")
        sector_revenue = df.groupby('sector')['total_price_etb'].sum().reset_index()
        
        fig1 = px.pie(sector_revenue, values='total_price_etb', names='sector', title='Total Revenue by Sector (ETB)', hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
        
        st.markdown("---")
        
        # 2. Top Producers by Sales
        st.subheader("🏆 Top Producers by Sales Volume")
        producer_sales = df.groupby('seller_name')['total_price_etb'].sum().reset_index().sort_values(by='total_price_etb', ascending=False).head(10)
        
        fig2 = px.bar(producer_sales, x='seller_name', y='total_price_etb', title='Top 10 Producers by Revenue (ETB)')
        fig2.update_traces(texttemplate='%{y:,.0f} ETB', textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        
        # 3. Most Popular Categories
        st.subheader("🛒 Most Popular Product Categories")
        category_counts = df['category'].value_counts().reset_index()
        category_counts.columns = ['category', 'count']
        
        fig3 = px.bar(category_counts, x='category', y='count', title='Order Volume by Product Category')
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("---")
        
        # 4. Highest Demand Regions
        st.subheader("📍 Highest Demand Regions (Cities)")
        city_demand = df['city'].value_counts().reset_index()
        city_demand.columns = ['city', 'count']
        
        fig4 = px.bar(city_demand, x='city', y='count', title='Order Volume by City')
        st.plotly_chart(fig4, use_container_width=True)
        
    except Exception as e:
        st.error(f"Failed to generate reports: {str(e)}")
