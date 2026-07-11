import streamlit as st
from utils.db import supabase
from utils.constants import CATEGORIES, SECTORS, UNIT_TYPES, ETHIOPIAN_CITIES, format_etb

def render_inventory():
    if st.session_state.get("role") != "producer":
        st.switch_page("app.py")
        
    st.title("📦 Inventory Management")
    
    user_id = st.session_state.get("user_id")
    
    # Add new product form
    with st.expander("➕ Add New Product", expanded=True):
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Product Name")
            category = col2.selectbox("Category", CATEGORIES)
            
            col3, col4 = st.columns(2)
            sector = col3.selectbox("Sector", SECTORS)
            
            # Default to user's city if available
            default_city = st.session_state.get("city", "Addis Ababa")
            city_idx = ETHIOPIAN_CITIES.index(default_city) if default_city in ETHIOPIAN_CITIES else 0
            city = col4.selectbox("City Location", ETHIOPIAN_CITIES, index=city_idx)
            
            col5, col6, col7 = st.columns(3)
            quantity = col5.number_input("Quantity", min_value=0.0, step=1.0)
            unit = col6.selectbox("Unit", UNIT_TYPES)
            price_etb = col7.number_input("Price per Unit (ETB)", min_value=0.0, step=10.0)
            
            submitted = st.form_submit_button("List Product", use_container_width=True)
            
            if submitted:
                if not name or quantity <= 0 or price_etb <= 0:
                    st.error("Please fill all fields with valid values.")
                else:
                    try:
                        supabase.table("products").insert({
                            "producer_id": user_id,
                            "name": name,
                            "category": category,
                            "sector": sector,
                            "quantity": quantity,
                            "unit": unit,
                            "price_etb": price_etb,
                            "city": city,
                            "status": "active"
                        }).execute()
                        st.success(f"Product '{name}' listed successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to list product: {str(e)}")
                        
    st.markdown("---")
    st.subheader("📋 Active Listings")
    
    try:
        res = supabase.table("products").select("*").eq("producer_id", user_id).order("created_at", desc=True).execute()
        products = res.data
        
        if not products:
            st.info("You haven't listed any products yet.")
        else:
            for p in products:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    col1.markdown(f"### {p['name']}")
                    col1.caption(f"{p['category']} | {p['sector']} | 📍 {p['city']}")
                    
                    col2.markdown(f"**Price:** {format_etb(p['price_etb'])} / {p['unit']}")
                    col2.markdown(f"**Stock:** {p['quantity']} {p['unit']}")
                    
                    status_color = "green" if p['status'] == 'active' else "gray"
                    col3.markdown(f"<p style='color:{status_color}; font-weight:bold;'>{p['status'].capitalize()}</p>", unsafe_allow_html=True)
                    
                    if p['status'] == 'active':
                        if col3.button("Deactivate", key=f"deact_{p['id']}"):
                            supabase.table("products").update({"status": "inactive"}).eq("id", p['id']).execute()
                            st.rerun()
                    else:
                        if col3.button("Reactivate", key=f"react_{p['id']}"):
                            supabase.table("products").update({"status": "active"}).eq("id", p['id']).execute()
                            st.rerun()
                        
    except Exception as e:
        st.error(f"Failed to load inventory: {str(e)}")
