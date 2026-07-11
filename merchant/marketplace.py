import streamlit as st
from utils.db import supabase
from utils.constants import CATEGORIES, SECTORS, ETHIOPIAN_CITIES, PAYMENT_METHODS, format_etb

def render_marketplace():
    if st.session_state.get("role") != "merchant":
        st.switch_page("app.py")
        
    st.title("🏪 Marketplace")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cat_filter = st.selectbox("Category", ["All"] + CATEGORIES)
    with col2:
        sec_filter = st.selectbox("Sector", ["All"] + SECTORS)
    with col3:
        city_filter = st.selectbox("City", ["All"] + ETHIOPIAN_CITIES)
    with col4:
        price_range = st.slider("Max Price (ETB)", 0, 1000000, 1000000, step=1000)
        
    # Fetch products
    try:
        query = supabase.table("products").select("*, profiles(name, rating)").eq("status", "active")
        if cat_filter != "All":
            query = query.eq("category", cat_filter)
        if sec_filter != "All":
            query = query.eq("sector", sec_filter)
        if city_filter != "All":
            query = query.eq("city", city_filter)
        query = query.lte("price_etb", price_range)
        
        res = query.execute()
        products = res.data
        
        if not products:
            st.info("No products found matching your filters.")
            return
            
        for p in products:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.markdown(f"### {p['name']}")
                col1.caption(f"{p['category']} | {p['sector']} | 📍 {p['city']}")
                seller_name = p.get('profiles', {}).get('name', 'Unknown')
                seller_rating = p.get('profiles', {}).get('rating', 0.0)
                col1.markdown(f"**Seller:** {seller_name} {'⭐' * int(seller_rating)}")
                
                col2.markdown(f"**Price:** {format_etb(p['price_etb'])} / {p['unit']}")
                col2.markdown(f"**Available:** {p['quantity']} {p['unit']}")
                
                with col3:
                    with st.expander("🛒 Place Order"):
                        qty = st.number_input("Quantity", min_value=0.1, step=1.0, key=f"qty_{p['id']}")
                        pay_method = st.selectbox("Payment Method", PAYMENT_METHODS, key=f"pay_{p['id']}")
                        if st.button("Confirm Order", key=f"order_{p['id']}", use_container_width=True):
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
                                    
                                    # Update product stock
                                    new_stock = p['quantity'] - qty
                                    supabase.table("products").update({"quantity": new_stock}).eq("id", p['id']).execute()
                                    
                                    st.success(f"Order placed! Total: {format_etb(total_price)}")
                                except Exception as e:
                                    st.error(f"Failed to place order: {str(e)}")
    except Exception as e:
        st.error(f"Failed to load marketplace: {str(e)}")
