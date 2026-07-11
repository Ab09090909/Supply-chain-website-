import streamlit as st
from utils.db import supabase
from engines.matching import find_matches
from shared.profile_card import render_profile_card

def render_merchant_matching():
    if st.session_state.get("role") != "producer":
        st.switch_page("app.py")
        
    st.title("🤝 Find Merchants")
    st.markdown("Discover merchants who are a great fit for your products based on sector, location, and market trends.")
    
    user_id = st.session_state.get("user_id")
    user_city = st.session_state.get("city", "Addis Ababa")
    
    # Get user's primary sector to provide context to the matching engine
    try:
        prod_res = supabase.table("products").select("sector").eq("producer_id", user_id).limit(1).execute()
        user_sector = prod_res.data[0]["sector"] if prod_res.data else "Agriculture"
    except Exception:
        user_sector = "Agriculture"
        
    # Fetch all merchants from the platform
    try:
        merchants_res = supabase.table("profiles").select("*").eq("role", "merchant").execute()
        merchants = merchants_res.data
        
        if not merchants:
            st.info("No merchants found on the platform yet.")
            return
            
        # Run matching engine
        user_profile = {"city": user_city, "role": "producer"}
        product_context = {"sector": user_sector}
        
        with st.spinner("🧠 AI is finding the best merchant matches..."):
            matched_merchants = find_matches(user_profile, product_context, merchants)
            
        st.success(f"Found {len(matched_merchants)} potential merchants!")
        
        for m in matched_merchants:
            render_profile_card(m, match_score=m.get("match_score", 0))
            
            # Contact action
            if st.button(f"💬 Send Inquiry to {m['name']}", key=f"contact_{m['id']}"):
                st.toast(f"Inquiry sent to {m['name']}! They will be notified.", icon="✅")
                
    except Exception as e:
        st.error(f"Failed to find merchants: {str(e)}")
