import streamlit as st
from utils.db import supabase
from engines.recommendation import get_recommendations
from utils.constants import format_etb

def render_customer_home():
    if st.session_state.get("role") != "customer":
        st.switch_page("app.py")
        
    st.title(f"👋 Welcome back, {st.session_state.get('name', 'Customer')}!")
    st.markdown("Discover amazing products from across Ethiopia.")
    
    user_id = st.session_state.get("user_id")
    
    try:
        # 1. Featured / Recent Products
        st.subheader("🆕 Recent Arrivals")
        recent_res = supabase.table("products").select("*, profiles(name, rating)").eq("status", "active").order("created_at", desc=True).limit(6).execute()
        recent_products = recent_res.data if recent_res.data else []
        
        if recent_products:
            cols = st.columns(3)
            for idx, p in enumerate(recent_products):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {p['name']}")
                        st.caption(f"{p['category']} | 📍 {p['city']}")
                        st.markdown(f"**Price:** {format_etb(p['price_etb'])} / {p['unit']}")
                        seller_name = p.get('profiles', {}).get('name', 'Unknown')
                        st.caption(f"Sold by: {seller_name}")
        else:
            st.info("No recent products available.")
            
        st.markdown("---")
        
        # 2. AI Recommendations
        st.subheader("✨ Picked For You")
        
        orders_res = supabase.table("orders").select("product_id").eq("buyer_id", user_id).execute()
        purchase_history = [o["product_id"] for o in orders_res.data] if orders_res.data else []
        
        products_res = supabase.table("products").select("id, name, category, price_etb, unit, city, profiles(name)").eq("status", "active").execute()
        all_products = products_res.data if products_res.data else []
        
        if all_products:
            all_product_ids = [p["id"] for p in all_products]
            recommended_ids = get_recommendations(user_id, purchase_history, all_product_ids)
            
            if not recommended_ids:
                recommended_ids = all_product_ids[:6]
                
            product_map = {p["id"]: p for p in all_products}
            recommended_products = [product_map[pid] for pid in recommended_ids[:6] if pid in product_map]
            
            cols = st.columns(3)
            for idx, p in enumerate(recommended_products):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {p['name']}")
                        st.caption(f"{p['category']} | 📍 {p['city']}")
                        st.markdown(f"**Price:** {format_etb(p['price_etb'])} / {p['unit']}")
                        seller_name = p.get('profiles', {}).get('name', 'Unknown')
                        st.caption(f"Sold by: {seller_name}")
        else:
            st.info("No recommendations available yet.")
            
    except Exception as e:
        st.error(f"Failed to load home page: {str(e)}")
