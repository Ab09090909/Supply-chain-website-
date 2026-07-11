import streamlit as st
from datetime import datetime
from utils.db import supabase
from utils.pdf import generate_agreement_pdf
from utils.constants import PAYMENT_METHODS

def render_agreement_creation(producer_id: str, merchant_id: str, product_id: str, product_name: str, price_etb: float, quantity: float, unit: str):
    """
    Renders a form to create and sign a trade agreement.
    """
    st.subheader("📝 Draft Trade Agreement")
    
    with st.form("agreement_form"):
        col1, col2 = st.columns(2)
        delivery_date = col1.date_input("Expected Delivery Date")
        payment_method = col2.selectbox("Payment Method", PAYMENT_METHODS)
        delivery_terms = st.text_area("Delivery Terms & Conditions", placeholder="e.g., FOB Addis Ababa, transport costs borne by merchant...")
        
        submitted = st.form_submit_button("Generate & Sign Agreement")
        
        if submitted:
            # Fetch names for PDF
            prod_res = supabase.table("profiles").select("name").eq("id", producer_id).execute()
            merch_res = supabase.table("profiles").select("name").eq("id", merchant_id).execute()
            
            prod_name = prod_res.data[0]["name"] if prod_res.data else "Unknown Producer"
            merch_name = merch_res.data[0]["name"] if merch_res.data else "Unknown Merchant"
            
            agreement_data = {
                "producer_name": prod_name,
                "merchant_name": merch_name,
                "product_name": product_name,
                "quantity": quantity,
                "unit": unit,
                "price_etb": price_etb * quantity,
                "delivery_terms": delivery_terms,
                "payment_method": payment_method
            }
            
            pdf_bytes = generate_agreement_pdf(agreement_data)
            
            # Save to DB
            terms_json = {
                "delivery_date": str(delivery_date),
                "payment_method": payment_method,
                "delivery_terms": delivery_terms
            }
            
            try:
                supabase.table("agreements").insert({
                    "producer_id": producer_id,
                    "merchant_id": merchant_id,
                    "product_id": product_id,
                    "terms_json": terms_json,
                    "signed_at": datetime.now().isoformat()
                }).execute()
                
                st.success("Agreement signed and saved!")
                st.download_button(
                    label="📥 Download Signed PDF",
                    data=pdf_bytes,
                    file_name=f"Agreement_{product_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Failed to save agreement: {str(e)}")
