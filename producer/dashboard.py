# producer/dashboard.py
import streamlit as st
import plotly.graph_objects as go
from utils.db import supabase
from utils.constants import format_etb, CATEGORIES, SECTORS
from utils.nav import render_sidebar
# Note: We import it just in case, but we don't call it here to avoid duplicates
from utils.chatbot import render_chatbot 
from engines.demand import get_demand_forecast

def main():
    # Verify producer role
    if "role" not in st.session_state or st.session_state.role != "producer":
        st.error("Access denied. Please login as a producer.")
        st.stop()
    
    # Render sidebar navigation
    render_sidebar()
    
    # Main content
    st.title("🏭 Producer Dashboard")
    st.markdown(f"**Welcome back, {st.session_state.name}** | 📍 {st.session_state.city}")
    st.write("Here is an overview of your production and sales performance.")
    
    # ==========================================
    # 🔍 SEARCH BAR - ALWAYS VISIBLE
    # ==========================================
    st.markdown("---")
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_query = st.text_input(
            "🔍 Search Products",
            placeholder="Search by name, category, or sector...",
            label_visibility="visible",
            key="product_search"
        )
    
    with search_col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "Active", "Inactive"],
            key="status_filter"
        )
    
    # Fetch all products
    try:
        response = supabase.table("products")\
            .select("*")\
            .eq("producer_id", st.session_state.user_id)\
            .execute()
        all_products = response.data or []
    except Exception as e:
        st.error(f"Error loading products: {str(e)}")
        all_products = []
    
    # Apply filters
    filtered_products = all_products.copy()
    
    if status_filter != "All":
        status_value = status_filter.lower() == "active"
        filtered_products = [p for p in filtered_products if p.get("status") == status_value]
    
    if search_query.strip():
        query = search_query.lower().strip()
        filtered_products = [
            p for p in filtered_products 
            if (query in p.get("name", "").lower() or
                query in p.get("category", "").lower() or
                query in p.get("sector", "").lower())
        ]
    
    # Show search results count
    if search_query.strip() or status_filter != "All":
        st.caption(f"Found {len(filtered_products)} product(s)")
    
    # ==========================================
    # METRICS CARD
    # ==========================================
    st.markdown("---")
    
    active_listings = len([p for p in all_products if p.get("status") == "active"])
    
    try:
        orders = supabase.table("orders")\
            .select("total_price_etb, status")\
            .eq("seller_id", st.session_state.user_id)\
            .execute().data or []
        total_orders = len(orders)
        total_revenue = sum(o.get("total_price_etb", 0) for o in orders if o.get("status") == "Completed")
    except:
        total_orders = 0
        total_revenue = 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Active Listings", active_listings)
    col2.metric(" Total Orders", total_orders)
    col3.metric("💰 Total Revenue", format_etb(total_revenue))
    
    # ==========================================
    # DISPLAY PRODUCTS
    # ==========================================
    st.markdown("---")
    st.subheader("📦 Your Products")
    
    if filtered_products:
        for i in range(0, len(filtered_products), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(filtered_products):
                    product = filtered_products[i + j]
                    with col:
                        with st.container(border=True):
                            st.markdown(f"**{product.get('name', 'Unnamed')}**")
                            st.caption(f"{product.get('category')} • {product.get('sector')}")
                            st.markdown(f"**💰 {format_etb(product.get('price_etb', 0))}**")
                            st.write(f"📦 {product.get('quantity')} {product.get('unit')}")
                            st.write(f"📍 {product.get('city')}")
                            status_icon = "🟢" if product.get("status") == "active" else "🔴"
                            st.write(f"{status_icon} {product.get('status', 'unknown').capitalize()}")
    elif search_query.strip():
        st.info(f" No products found matching '{search_query}'")
    else:
        st.info("📦 You haven't added any products yet. Click the Inventory tab to add your first product!")
    
    # ==========================================
    # DEMAND FORECAST
    # ==========================================
    st.markdown("---")
    st.subheader("📊 30-Day Demand Forecast")
    
    if all_products:
        categories = list(set(p.get("category") for p in all_products if p.get("category")))
        if categories:
            selected_cat = st.selectbox("Select category", categories, key="forecast_cat")
            try:
                forecast = get_demand_forecast(
                    category=selected_cat,
                    sector=SECTORS[0],
                    region=st.session_state.city
                )
                if forecast:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=list(range(1, len(forecast) + 1)),
                        y=forecast,
                        mode='lines+markers',
                        line=dict(color='#00A859', width=3)
                    ))
                    fig.update_layout(
                        title=f"Demand for {selected_cat} in {st.session_state.city}",
                        xaxis_title="Days",
                        yaxis_title="Demand Index",
                        template='plotly_dark',
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Forecast error: {str(e)}")
    else:
        st.info("Add products to see demand forecasts")
    
    # NOTE: We do NOT call render_chatbot() here. 
    # It is called in pages/1_producer.py to prevent duplicate chatbots.
