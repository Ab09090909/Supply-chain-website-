import streamlit as st
from utils.db import supabase
from utils.constants import format_etb

def render_favorites():
    if st.session_state.get("role") != "customer":
        st.switch_page("app.py")
        
    st.title("❤️ My Favorites")
    st.markdown("Products you've saved for later.")
    
    user_id = st.session_state.get("user_id")
    
    try:
        # Fetch favorites with product and seller details
        res = supabase.table("favorites").select("*, products(*, profiles(name, rating))").eq("customer_id", user_id).order("created_at", desc=True).execute()
        favorites = res.data
        
        if not favorites:
            st.info("You haven't saved any products yet. Browse the marketplace to find items you love!")
            return
            
        # Display in a responsive grid
        cols = st.columns(3)
        for idx, fav in enumerate(favorites):
            with cols[idx % 3]:
                p = fav["products"]
                with st.container(border=True):
                    st.markdown(f"### {p['name']}")
                    st.caption(f"{p['category']} | 📍 {p['city']}")
                    st.markdown(f"**Price:** {format_etb(p['price_etb'])} / {p['unit']}")
                    
                    seller_name = p.get('profiles', {}).get('name', 'Unknown')
                    seller_rating = p.get('profiles', {}).get('rating', 0.0)
                    st.caption(f"Sold by: {seller_name} {'⭐' * int(seller_rating)}")
                    
                    if st.button("🗑️ Remove", key=f"remove_{fav['id']}", use_container_width=True):
                        supabase.table("favorites").delete().eq("id", fav["id"]).execute()
                        st.rerun()
                        
    except Exception as e:
        st.error(f"Failed to load favorites: {str(e)}")
