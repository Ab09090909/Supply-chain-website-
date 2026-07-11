import streamlit as st
from utils.db import supabase
from utils.constants import format_etb

def render_orders_list(user_id: str, role: str):
    """
    Renders a list of orders for the given user.
    Handles status updates based on role.
    """
    st.subheader("📦 My Orders")
    
    try:
        # Fetch orders where user is buyer or seller
        res = supabase.table("orders").select("*, products(name, category)").or_(f"buyer_id.eq.{user_id},seller_id.eq.{user_id}").order("created_at", desc=True).execute()
        orders = res.data
        
        if not orders:
            st.info("No orders found.")
            return
            
        for order in orders:
            with st.expander(f"Order #{order['id'][:8]} - {order['products']['name']} | {format_etb(order['total_price_etb'])} | Status: {order['status']}"):
                col1, col2 = st.columns(2)
                col1.write(f"**Quantity:** {order['quantity']}")
                col1.write(f"**Payment:** {order['payment_method']}")
                col2.write(f"**Category:** {order['products']['category']}")
                col2.write(f"**Date:** {order['created_at'][:10]}")
                
                # Status update logic
                if role == "merchant" and order["status"] == "Pending":
                    if st.button("Confirm Order", key=f"confirm_{order['id']}"):
                        supabase.table("orders").update({"status": "Confirmed"}).eq("id", order["id"]).execute()
                        st.rerun()
                elif role == "producer" and order["status"] == "Confirmed":
                    if st.button("Mark as Shipped", key=f"ship_{order['id']}"):
                        supabase.table("orders").update({"status": "Shipped"}).eq("id", order["id"]).execute()
                        st.rerun()
                elif role == "merchant" and order["status"] == "Shipped":
                    if st.button("Mark as Delivered", key=f"deliver_{order['id']}"):
                        supabase.table("orders").update({"status": "Delivered"}).eq("id", order["id"]).execute()
                        st.rerun()
                        
    except Exception as e:
        st.error(f"Failed to load orders: {str(e)}")
