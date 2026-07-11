import streamlit as st
from utils.db import supabase
from utils.constants import format_etb
from shared.demand import render_demand_forecast

def render_producer_dashboard():
    if st.session_state.get("role") != "producer":
        st.switch_page("app.py")
        
    st.title(f"👋 Welcome, {st.session_state.get('name', 'Producer')}")
    st.markdown("Here is an overview of your production and sales performance.")
    
    user_id = st.session_state.get("user_id")
    
    # Fetch key metrics
    try:
        # Active listings count
        prod_res = supabase.table("products").select("id").eq("producer_id", user_id).eq("status", "active").execute()
        active_listings = len(prod_res.data) if prod_res.data else 0
        
        # Total orders and revenue (only count delivered/completed for revenue)
        orders_res = supabase.table("orders").select("total_price_etb, status").eq("seller_id", user_id).execute()
        orders = orders_res.data if orders_res.data else []
        
        total_orders = len(orders)
        total_revenue = sum(o["total_price_etb"] for o in orders if o["status"] in ["Delivered", "Completed"])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Active Listings", active_listings)
        col2.metric("🛒 Total Orders", total_orders)
        col3.metric("💰 Total Revenue", format_etb(total_revenue))
        
    except Exception as e:
        st.error(f"Failed to load dashboard metrics: {str(e)}")
        
    st.markdown("---")
    
    # Determine primary category/sector for the demand forecast
    try:
        prod_res = supabase.table("products").select("sector, category").eq("producer_id", user_id).execute()
        if prod_res.data:
            sectors = [p["sector"] for p in prod_res.data]
            categories = [p["category"] for p in prod_res.data]
            top_sector = max(set(sectors), key=sectors.count)
            top_category = max(set(categories), key=categories.count)
        else:
            top_sector = "Agriculture"
            top_category = "Grains"
    except Exception:
        top_sector = "Agriculture"
        top_category = "Grains"
        
    # Render the shared 30-day demand forecast chart
    render_demand_forecast(
        category=top_category, 
        sector=top_sector, 
        region=st.session_state.get("city", "Addis Ababa")
    )
