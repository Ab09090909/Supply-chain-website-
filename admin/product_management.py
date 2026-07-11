import streamlit as st
import pandas as pd
from utils.db import supabase
from utils.constants import format_etb

def render_product_management():
    if st.session_state.get("role") != "admin":
        st.switch_page("app.py")
        
    st.title("📦 Product Management")
    
    try:
        res = supabase.table("products").select("*, profiles(name)").order("created_at", desc=True).execute()
        products = res.data
        
        if not products:
            st.info("No products found.")
            return
            
        df = pd.DataFrame(products)
        df['seller_name'] = df['profiles'].apply(lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else 'Unknown')
        df['price_display'] = df['price_etb'].apply(format_etb)
        
        st.dataframe(df[['name', 'seller_name', 'category', 'sector', 'price_display', 'city', 'status']], use_container_width=True)
        
        st.markdown("---")
        st.subheader("⚙️ Product Actions")
        
        product_ids = [p["id"] for p in products]
        selected_product = st.selectbox("Select Product to Manage", product_ids, format_func=lambda x: f"{x} ({next((p['name'] for p in products if p['id'] == x), 'Unknown')})")
        
        if selected_product:
            col1, col2, col3 = st.columns(3)
            
            if col1.button("✅ Approve / Activate", use_container_width=True):
                supabase.table("products").update({"status": "active"}).eq("id", selected_product).execute()
                st.success("Product activated!")
                st.rerun()
                
            if col2.button("🙈 Hide / Deactivate", use_container_width=True):
                supabase.table("products").update({"status": "inactive"}).eq("id", selected_product).execute()
                st.success("Product hidden!")
                st.rerun()
                
            if col3.button("🗑️ Delete Product", use_container_width=True):
                supabase.table("products").delete().eq("id", selected_product).execute()
                st.success("Product deleted!")
                st.rerun()
                
    except Exception as e:
        st.error(f"Failed to load products: {str(e)}")
