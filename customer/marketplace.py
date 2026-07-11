import streamlit as st
from utils.db import supabase
from utils.constants import CATEGORIES, ETHIOPIAN_CITIES, PAYMENT_METHODS, format_etb

def render_customer_marketplace():
    if st.session_state.get("role") != "customer":
        st.switch_page("app.py")
        
    st.title("🛍️ Marketplace")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_query = st.text_input("🔍 Search", placeholder="e.g., Teff, Coffee...")
    with col2:
        cat_filter = st.selectbox("Category", ["All"] + CATEGORIES)
    with col3:
        city_filter = st.selectbox("City", ["All"] + ETHIOPIAN_CITIES)
    with col4:
        price_range = st.slider("Max Price (ETB)", 0, 500000, 500000, step=1000)
        
    try:
        query = supabase.table("products").select("*, profiles(name, rating)").eq("status", "active")
        
        if search_query:
            query = query.ilike("name", f"%{search_query}%")
        if cat_filter != "All":
            query = query.eq("category", cat_filter)
        if city_filter != "All":
            query = query.eq("city", city_filter)
        query = query.lte("price_etb", price_range)
        
        res = query.execute()
        products = res.data
        
        if not products:
            st.info("No products found matching your criteria.")
            return
            
        cols = st.columns(3)
        for idx, p in enumerate(products):
            with cols[idx % 3]:
                with st.container(border=True):
                    # Image placeholder
                    st.image("https://via.placeholder.com/300x200?text=Product+Image", use_container_width=True)
                    
                    st.markdown(f"### {p['name']}")
                    st.caption(f"{p['category']} | 📍 {p['city']}")
                    st.markdown(f"**Price:** {format_etb(p['price_etb'])} / {p['unit']}")
                    
                    seller_name = p.get('profiles', {}).get('name', 'Unknown')
                    seller_rating = p.get('profiles', {}).get('rating', 0.0)
                    st.caption(f"Sold by: {seller_name} {'⭐' * int(seller_rating)}")
                    
                    # Quick buy modal
                    with st.expander("🛒 Quick Buy"):
                        qty = st.number_input("Quantity", min_value=1.0, step=1.0, key=f"qty_c_{p['id']}")
                        pay_method = st.selectbox("Payment", PAYMENT_METHODS, key=f"pay_c_{p['id']}")
                        
                        if st.button("Confirm Purchase", key=f"order_c_{p['id']}", use_container_width=True):
                            if qty > p['quantity']:
                                st.error("Not enough stock available.")
                            else:
                                total_price = qty * p['price_etb']
                                try:
                                    supabase.table("orders").insert({
                                        "buyer_id": st.session_state.user_id,
                                        "seller_id": p['producer_id'],
                                        "product_id": p['id'],
                                        "quantity": qty,
                                        "total_price_etb": total_price,
                                        "status": "Pending",
                                        "payment_method": pay_method
                                    }).execute()
                                    
                                    new_stock = p['quantity'] - qty
                                    supabase.table("products").update({"quantity": new_stock}).eq("id", p['id']).execute()
                                    
                                    st.success(f"Order placed! Total: {format_etb(total_price)}")
                                except Exception as e:
                                    st.error(f"Failed to place order: {str(e)}")
                                    
                    # Save to favorites
                    if st.button("❤️ Save to Favorites", key=f"fav_c_{p['id']}", use_container_width=True):
                        try:
                            existing = supabase.table("favorites").select("id").eq("customer_id", st.session_state.user_id).eq("product_id", p['id']).execute()
                            if not existing.data:
                                supabase.table("favorites").insert({
                                    "customer_id": st.session_state.user_id,
                                    "product_id": p['id']
                                }).execute()
                                st.toast("Added to favorites!", icon="❤️")
                            else:
                                st.toast("Already in favorites.", icon="ℹ️")
                        except Exception as e:
                            st.error(f"Failed to save favorite: {str(e)}")
                            
    except Exception as e:
        st.error(f"Failed to load marketplace: {str(e)}")
