import streamlit as st
from utils.db import supabase
from engines.matching import find_matches
from shared.profile_card import render_profile_card

def render_producer_matching():
    if st.session_state.get("role") != "merchant":
        st.switch_page("app.py")
        
    st.title("🤝 Find Producers")
    st.markdown("Discover suppliers who are a great fit for your business based on sector, location, and market trends.")
    
    user_id = st.session_state.get("user_id")
    user_city = st.session_state.get("city", "Addis Ababa")
    
    # Get user's primary sector from past orders or default
    try:
        orders_res = supabase.table("orders").select("products(sector)").eq("buyer_id", user_id).limit(5).execute()
        sectors = [o["products"]["sector"] for o in orders_res.data if "products" in o]
        user_sector = max(set(sectors), key=sectors.count) if sectors else "Agriculture"
    except Exception:
        user_sector = "Agriculture"
        
    try:
        producers_res = supabase.table("profiles").select("*").eq("role", "producer").execute()
        producers = producers_res.data
        
        if not producers:
            st.info("No producers found on the platform yet.")
            return
            
        user_profile = {"city": user_city, "role": "merchant"}
        product_context = {"sector": user_sector}
        
        with st.spinner("🧠 AI is finding the best producer matches..."):
            matched_producers = find_matches(user_profile, product_context, producers)
            
        st.success(f"Found {len(matched_producers)} potential producers!")
        
        for p in matched_producers:
            render_profile_card(p, match_score=p.get("match_score", 0))
            
            if st.button(f"💬 Send Inquiry to {p['name']}", key=f"contact_{p['id']}"):
                st.toast(f"Inquiry sent to {p['name']}! They will be notified.", icon="✅")
                
    except Exception as e:
        st.error(f"Failed to find producers: {str(e)}")
