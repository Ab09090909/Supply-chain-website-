# producer/dashboard.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.db import supabase
from utils.constants import format_etb, CATEGORIES, SECTORS
from utils.nav import render_sidebar
from utils.chatbot import render_chatbot
from engines.demand import get_demand_forecast

def main():
    st.set_page_config(
        page_title="Producer Dashboard - EthioChain",
        page_icon="🏭",
        layout="wide"
    )
    
    # Verify producer role
    if "role" not in st.session_state or st.session_state.role != "producer":
        st.error("Access denied. Please login as a producer.")
        st.stop()
    
    # Render sidebar navigation
    render_sidebar()
    
    # Main content
    st.title("🏭 Producer Dashboard")
    st.markdown(f"**Welcome back, {st.session_state.name}** | 📍 {st.session_state.city}")
    st.divider()
    
    # === PRODUCT SEARCH BAR ===
    st.subheader("🔍 Search Your Products")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search products by name or category",
            placeholder="Enter product name, category, or sector...",
            label_visibility="collapsed"
        )
    
    with col2:
        search_filter = st.selectbox(
            "Filter by",
            ["All", "Active", "Inactive"],
            label_visibility="collapsed"
        )
    
    # Fetch and filter products
    try:
        # Base query
        query = supabase.table("products").select("*").eq("producer_id", st.session_state.user_id)
        
        # Apply status filter
        if search_filter == "Active":
            query = query.eq("status", "active")
        elif search_filter == "Inactive":
            query = query.eq("status", "inactive")
        
        response = query.execute()
        all_products = response.data
        
        # Apply search filter
        if search_query:
            search_lower = search_query.lower()
            filtered_products = [
                p for p in all_products 
                if search_lower in p.get("name", "").lower() or
                   search_lower in p.get("category", "").lower() or
                   search_lower in p.get("sector", "").lower()
            ]
        else:
            filtered_products = all_products
        
    except Exception as e:
        st.error(f"Error loading products: {str(e)}")
        filtered_products = []
        all_products = []
    
    # === DASHBOARD METRICS ===
    st.divider()
    st.subheader("📊 Overview")
    
    # Calculate metrics from all products (not just filtered)
    active_listings = len([p for p in all_products if p.get("status") == "active"])
    total_products = len(all_products)
    
    # Calculate total revenue from orders
    try:
        orders_response = supabase.table("orders")\
            .select("total_price_etb")\
            .eq("seller_id", st.session_state.user_id)\
            .eq("status", "Completed")\
            .execute()
        total_revenue = sum(order.get("total_price_etb", 0) for order in orders_response.data)
    except Exception:
        total_revenue = 0
    
    # Calculate total orders
    try:
        total_orders = len(supabase.table("orders")\
            .select("id")\
            .eq("seller_id", st.session_state.user_id)\
            .execute().data)
    except Exception:
        total_orders = 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Listings", active_listings)
    with col2:
        st.metric("Total Products", total_products)
    with col3:
        st.metric("Total Orders", total_orders)
    with col4:
        st.metric("Total Revenue", format_etb(total_revenue))
    
    # === SEARCH RESULTS ===
    st.divider()
    st.subheader(f" Your Products {'(' + str(len(filtered_products)) + ' found)' if search_query else ''}")
    
    if filtered_products:
        # Display products in a grid
        for i in range(0, len(filtered_products), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(filtered_products):
                    product = filtered_products[i + j]
                    with col:
                        with st.container(border=True):
                            st.markdown(f"**{product.get('name', 'Unnamed Product')}**")
                            st.caption(f" {product.get('category', 'N/A')} | 🏭 {product.get('sector', 'N/A')}")
                            st.markdown(f"**💰 {format_etb(product.get('price_etb', 0))}**")
                            st.markdown(f"📦 {product.get('quantity', 0)} {product.get('unit', 'units')}")
                            st.markdown(f" {product.get('city', 'N/A')}")
                            
                            status_color = "" if product.get("status") == "active" else "🔴"
                            st.markdown(f"{status_color} {product.get('status', 'unknown').capitalize()}")
                            
                            # Quick actions
                            col_edit, col_view = st.columns(2)
                            with col_edit:
                                if st.button("✏️ Edit", key=f"edit_{product.get('id')}"):
                                    st.switch_page("producer/inventory.py")
                            with col_view:
                                if st.button("📊 View", key=f"view_{product.get('id')}"):
                                    st.session_state.selected_product = product
                                    st.rerun()
    else:
        if search_query:
            st.info(f"No products found matching '{search_query}'. Try a different search term.")
        else:
            st.info("You haven't added any products yet. Go to Inventory to add your first product!")
            if st.button("➕ Add Product"):
                st.switch_page("producer/inventory.py")
    
    # === DEMAND FORECAST CHART ===
    st.divider()
    st.subheader(" Demand Forecast")
    
    if all_products:
        # Get the most common category or use the first product's category
        categories = [p.get("category") for p in all_products if p.get("category")]
        selected_category = st.selectbox(
            "Select product category for forecast",
            options=list(set(categories)) if categories else CATEGORIES
        )
        
        try:
            forecast_data = get_demand_forecast(
                category=selected_category,
                sector=SECTORS[0] if SECTORS else "Agriculture",
                region=st.session_state.city
            )
            
            if forecast_data and len(forecast_data) > 0:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(range(len(forecast_data))),
                    y=forecast_data,
                    mode='lines+markers',
                    name='Predicted Demand',
                    line=dict(color='#00A859', width=3),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title=f"30-Day Demand Forecast for {selected_category}",
                    xaxis_title="Days",
                    yaxis_title="Demand Index",
                    hovermode='x unified',
                    template='plotly_dark',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No forecast data available for this category.")
                
        except Exception as e:
            st.error(f"Error loading forecast: {str(e)}")
    else:
        st.info("Add products to see demand forecasts for your categories.")
    
    # Render floating chatbot
    render_chatbot()

if __name__ == "__main__":
    main()
