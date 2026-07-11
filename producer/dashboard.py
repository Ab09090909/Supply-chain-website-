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
        prod_res = supabase.table("products").select("id").eq("producer_id", user_id).eq("status", "active").execute()
        active_listings = len(prod_res.data) if prod_res.data else 0
        
        orders_res = supabase.table("orders").select("total_price_etb, status").eq("seller_id", user_id).execute()
        orders = orders_res.data if orders_res.data else []
        
        total_orders = len(orders)
        total_revenue = sum(o["total_price_etb"] for o in orders if o["status"] in ["Delivered", "Completed"])
        
        # --- MODERNIZED SINGLE BOX METRICS ---
        st.markdown("""
        <style>
        /* The main unified card */
        .modern-stats-card {
            background: linear-gradient(135deg, #1a1d29 0%, #232736 100%);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid #2E86C1;
            box-shadow: 0 8px 24px rgba(46, 134, 193, 0.15);
            margin-bottom: 30px;
        }
        /* Individual metric styling */
        .metric-item {
            text-align: center;
            padding: 10px;
        }
        .metric-label {
            color: #a0a0a0;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-value {
            color: #ffffff;
            font-size: 32px;
            font-weight: 700;
            margin: 0;
        }
        .metric-icon {
            font-size: 24px;
            margin-bottom: 10px;
        }
        /* Divider between metrics */
        .metric-divider {
            width: 1px;
            background-color: #2E86C1;
            opacity: 0.3;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Render the unified card
        st.markdown('<div class="modern-stats-card">', unsafe_allow_html=True)
        
        col1, div1, col2, div2, col3 = st.columns([1, 0.05, 1, 0.05, 1])
        
        with col1:
            st.markdown(f"""
                <div class="metric-item">
                    <div class="metric-icon">📦</div>
                    <div class="metric-label">Active Listings</div>
                    <div class="metric-value">{active_listings}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with div1:
            st.markdown('<div class="metric-divider"></div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="metric-item">
                    <div class="metric-icon">🛒</div>
                    <div class="metric-label">Total Orders</div>
                    <div class="metric-value">{total_orders}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with div2:
            st.markdown('<div class="metric-divider"></div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class="metric-item">
                    <div class="metric-icon"></div>
                    <div class="metric-label">Total Revenue</div>
                    <div class="metric-value">{format_etb(total_revenue)}</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        # ---------------------------------------
        
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
