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
        
        # --- HORIZONTAL FLEXBOX METRICS ---
        # We use pure HTML/CSS Flexbox to force them side-by-side, 
        # bypassing Streamlit's mobile stacking behavior.
        
        metrics_html = f"""
        <style>
        .stats-row-container {{
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(135deg, #1a1d29 0%, #232736 100%);
            border-radius: 16px;
            padding: 20px 10px;
            border: 1px solid #2E86C1;
            box-shadow: 0 8px 24px rgba(46, 134, 193, 0.15);
            margin-bottom: 30px;
            width: 100%;
            box-sizing: border-box;
        }}
        .stat-box {{
            flex: 1;
            text-align: center;
            padding: 10px 5px;
            border-right: 1px solid rgba(46, 134, 193, 0.3);
        }}
        .stat-box:last-child {{
            border-right: none;
        }}
        .stat-icon {{
            font-size: 24px;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #a0a0a0;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}
        .stat-value {{
            color: #ffffff;
            font-size: 22px;
            font-weight: 700;
        }}
        /* Mobile adjustment: allow wrapping if screen is extremely small */
        @media (max-width: 400px) {{
            .stats-row-container {{
                flex-wrap: wrap;
            }}
            .stat-box {{
                flex: 1 1 30%; /* Try to keep 3 in a row, but allow wrap */
                border-right: none;
                border-bottom: 1px solid rgba(46, 134, 193, 0.3);
                padding: 15px 0;
            }}
            .stat-box:last-child {{
                border-bottom: none;
            }}
        }}
        </style>
        
        <div class="stats-row-container">
            <div class="stat-box">
                <div class="stat-icon">📦</div>
                <div class="stat-label">Active Listings</div>
                <div class="stat-value">{active_listings}</div>
            </div>
            <div class="stat-box">
                <div class="stat-icon">🛒</div>
                <div class="stat-label">Total Orders</div>
                <div class="stat-value">{total_orders}</div>
            </div>
            <div class="stat-box">
                <div class="stat-icon"></div>
                <div class="stat-label">Total Revenue</div>
                <div class="stat-value">{format_etb(total_revenue)}</div>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)
        # ------------------------------------
        
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
