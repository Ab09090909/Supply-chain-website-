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
    st.title(" Producer Dashboard")
    st.markdown(f"**Welcome back, {st.session_state.name}** | 📍 {st.session_state.city}")
    st.write("Here is an overview of your production and sales performance.")
    
    # ==========================================
    # 🔍 PRODUCT SEARCH BAR
    # ==========================================
    st.markdown("---")
    st.subheader("🔍 Search Your Products")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input(
            "Search by product name, category, or sector",
            placeholder="e.g., Teff, Grains, Agriculture...",
            label_visibility="collapsed"
        )
    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "Active", "Inactive"],
            label_visibility="collapsed"
        )
    
    # Fetch and filter products
    try:
        response = supabase.table("products")\
            .select("*")\
            .eq("producer_id", st.session_state.user_id)\
            .execute()
        
        all_products = response.data
        
        # Apply filters
        filtered_products = all_products
        
        if status_filter != "All":
            status_bool = status_filter.lower() == "active"
            filtered_products = [p for p in filtered_products if p.get("status") == status_bool]
        
        if search_query:
            query_lower = search_query.lower()
            filtered_products = [
                p for p in filtered_products 
                if query_lower in p.get("name", "").lower() 
                or query_lower in p.get("category", "").lower()
                or query_lower in p.get("sector", "").lower()
            ]
        
    except Exception as e:
        st.error(f"Error loading products: {str(e)}")
        filtered_products = []
        all_products = []
    
    # Display search results
    if search_query or status_filter != "All":
        st.markdown(f"**Found {len(filtered_products)} product(s)**")
    
    # ==========================================
    # DASHBOARD METRICS
    # ==========================================
    st.markdown("---")
    st.subheader(" Overview")
    
    # Calculate metrics from all products
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
    
    # Display metrics in a card
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="📦 Active Listings",
                value=active_listings,
                delta=None
            )
        with col2:
            st.metric(
                label="🛒 Total Orders",
                value=total_orders,
                delta=None
            )
        with col3:
            st.metric(
                label="💰 Total Revenue",
                value=format_etb(total_revenue),
                delta=None
            )
    
    # ==========================================
    # SEARCH RESULTS DISPLAY
    # ==========================================
    if filtered_products:
        st.markdown("---")
        st.subheader("📦 Your Products")
        
        # Display products in expandable sections
        for product in filtered_products:
            with st.expander(f"📦 {product.get('name')} - {format_etb(product.get('price_etb', 0))}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Category:** {product.get('category')}")
                    st.write(f"**Sector:** {product.get('sector')}")
                    st.write(f"**Quantity:** {product.get('quantity')} {product.get('unit')}")
                with col2:
                    st.write(f"**Location:** {product.get('city')}")
                    status_emoji = "🟢" if product.get("status") == "active" else "🔴"
                    st.write(f"**Status:** {status_emoji} {product.get('status', 'unknown')}")
                    st.write(f"**Created:** {product.get('created_at', 'N/A')[:10] if product.get('created_at') else 'N/A'}")
                
                # Quick actions
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button("️ Edit Product", key=f"edit_{product.get('id')}"):
                        st.session_state.selected_product = product
                        st.switch_page("producer/inventory.py")
                with col_delete:
                    if st.button("🗑️ Deactivate", key=f"deact_{product.get('id')}"):
                        try:
                            supabase.table("products")\
                                .update({"status": "inactive"})\
                                .eq("id", product.get('id'))\
                                .execute()
                            st.success("Product deactivated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    elif search_query:
        st.info(f"No products found matching '{search_query}'. Try a different search term.")
    
    # ==========================================
    # DEMAND FORECAST CHART
    # ==========================================
    st.markdown("---")
    st.subheader(" 30-Day Demand Forecast")
    
    if all_products:
        # Get categories from producer's products
        categories = list(set([p.get("category") for p in all_products if p.get("category")]))
        
        if categories:
            selected_category = st.selectbox(
                "Select product category for forecast",
                options=categories,
                index=0
            )
            
            # Get sector from first product in that category
            sector = next((p.get("sector") for p in all_products if p.get("category") == selected_category), SECTORS[0])
            
            try:
                forecast_data = get_demand_forecast(
                    category=selected_category,
                    sector=sector,
                    region=st.session_state.city
                )
                
                if forecast_data and len(forecast_data) > 0:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=list(range(1, len(forecast_data) + 1)),
                        y=forecast_data,
                        mode='lines+markers',
                        name='Predicted Demand',
                        line=dict(color='#00A859', width=3),
                        marker=dict(size=8, color='#00A859')
                    ))
                    
                    fig.update_layout(
                        title=f"Demand Forecast for {selected_category} in {st.session_state.city}",
                        xaxis_title="Days",
                        yaxis_title="Demand Index",
                        hovermode='x unified',
                        template='plotly_dark',
                        height=400,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Forecast insights
                    avg_demand = sum(forecast_data) / len(forecast_data)
                    trend = "increasing" if forecast_data[-1] > forecast_data[0] else "decreasing"
                    st.info(f"📊 Average demand: {avg_demand:.1f} | Trend: {trend}")
                else:
                    st.warning("No forecast data available for this category.")
                    
            except Exception as e:
                st.error(f"Error loading forecast: {str(e)}")
        else:
            st.info("Add products to see demand forecasts.")
    else:
        st.info("📦 You haven't added any products yet. Go to Inventory to add your first product!")
        if st.button("➕ Add Your First Product"):
            st.switch_page("producer/inventory.py")
    
    # Render floating chatbot
    render_chatbot()

if __name__ == "__main__":
    main()
