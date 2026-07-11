import streamlit as st
from utils.db import supabase
from engines.recommendation import get_recommendations
from utils.constants import format_etb

def render_recommendations():
    if st.session_state.get("role") != "customer":
        st.switch_page("app.py")
        
    st.title("✨ Recommended For You")
    st.markdown("Products picked just for you based on your shopping history and preferences.")
    
    user_id = st.session_state.get("user_id")
    
    try:
        # Get purchase history
        orders_res = supabase.table("orders").select("product_id").eq("buyer_id", user_id).execute()
        purchase_history = [o["product_id"] for o in orders_res.data] if orders_res.data else []
        
        # Get all active products
        products_res = supabase.table("products").select("id, name, category, price_etb, unit, city, profiles(name, rating)").eq("status", "active").execute()
        all_products = products_res.data if products_res.data else []
        
        if not all_products:
            st.info("No products available in the marketplace right now.")
            return
            
        all_product_ids = [p["id"] for p in all_products]
        
        with st.spinner("🧠 AI is finding the best products for you..."):
            recommended_ids = get_recommendations(user_id, purchase_history, all_product_ids)
            
        if not recommended_ids:
            st.info("No specific recommendations at the moment. Check out our latest arrivals below!")
            recommended_ids = all_product_ids[:10] # Fallback to recent
            
        # Map IDs back to product objects
        product_map = {p["id"]: p for p in all_products}
        recommended_products = [product_map[pid] for pid in recommended_ids if pid in product_map]
        
        cols = st.columns(3)
        for idx, p in enumerate(recommended_products):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### {p['name']}")
                    st.caption(f"{p['category']} | 📍 {p['city']}")
                    st.markdown(f"**Price:** {format_etb(p['price_etb'])} / {p['unit']}")
                    
                    seller_name = p.get('profiles', {}).get('name', 'Unknown')
                    seller_rating = p.get('profiles', {}).get('rating', 0.0)
                    st.caption(f"Sold by: {seller_name} {'⭐' * int(seller_rating)}")
                    
                    if st.button("🛒 Buy Now", key=f"buy_rec_{p['id']}", use_container_width=True):
                        st.session_state[f"buy_product_{p['id']}"] = True
                        st.rerun()
                        
    except Exception as e:
        st.error(f"Failed to load recommendations: {str(e)}")
