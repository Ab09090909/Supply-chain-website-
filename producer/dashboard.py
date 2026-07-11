import streamlit as st
from utils.db import supabase
from utils.constants import format_etb
from shared.demand import render_demand_forecast

def render_producer_dashboard():
    if st.session_state.get("role") != "producer":
        st.switch_page("app.py")
        
    # --- UPDATE 1: Floating Search Bar CSS & HTML ---
    st.markdown("""
    <style>
    /* Floating Top Bar */
    .floating-search-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #0f1117; /* Matches your dark theme */
        padding: 12px 20px;
        z-index: 1000;
        border-bottom: 2px solid #2E86C1;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    /* Push content down so it's not hidden behind the fixed bar */
    .block-container {
        padding-top: 80px !important;
    }
    /* Compact Metric Boxes */
    .metric-box {
        background-color: #1a1d29;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #2E86C1;
        margin: 5px;
    }
    </style>
    
    <div class="floating-search-container">
    """, unsafe_allow_html=True)
    
    # The actual search input inside the fixed div
    search_query = st.text_input(
        " Search products, orders, or merchants...", 
        label_visibility="collapsed", 
        key="global_search_bar"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    # ------------------------------------------------

    st.title(f"👋 Welcome, {st.session_state.get('name', 'Producer')}")
    st.markdown("Here is an overview of your production and sales performance.")
    
    user_id = st.session_state.get("user_id")
    
    # Fetch key metrics
    try:
        prod_res = supabase.table("products").select("id").eq("producer_id", user_id).eq("status", "active").execute()
        active_listings = len(prod_res.data) if prod_res.data else 0
        
        orders_res = supabase.table("orders").select("total_price_etb, status").eq("seller_id", user_id).execute()
        orders = orders_res.data if orders_res.data else []
        
        total_orders = len(orders)
        total_revenue = sum(o["total_price_etb"] for o in orders if o["status"] in ["Delivered", "Completed"])
        
        # --- UPDATE 2: Compact Metrics in One Row ---
        # Using st.columns to force them side-by-side to reduce vertical space
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("📦 Active Listings", active_listings)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("🛒 Total Orders", total_orders)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric(" Total Revenue", format_etb(total_revenue))
            st.markdown('</div>', unsafe_allow_html=True)
        # ------------------------------------------------
        
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
