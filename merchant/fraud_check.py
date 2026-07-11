import streamlit as st
from engines.fraud import predict_fraud
from utils.constants import CATEGORIES, PAYMENT_METHODS, ETHIOPIAN_CITIES

def render_fraud_check():
    if st.session_state.get("role") != "merchant":
        st.switch_page("app.py")
        
    st.title("🛡️ Fraud Risk Analysis")
    st.markdown("Analyze the risk level of a transaction or supplier before proceeding.")
    
    with st.form("fraud_check_form"):
        col1, col2 = st.columns(2)
        amount = col1.number_input("Transaction Amount (ETB)", min_value=0.0, step=100.0)
        payment_method = col2.selectbox("Payment Method", PAYMENT_METHODS)
        
        col3, col4 = st.columns(2)
        category = col3.selectbox("Product Category", CATEGORIES)
        city = col4.selectbox("City", ETHIOPIAN_CITIES)
        
        supplier_id = st.text_input("Supplier ID (Optional)", placeholder="e.g., prod_12345")
        
        submitted = st.form_submit_button("Analyze Risk", use_container_width=True)
        
        if submitted:
            transaction = {
                "amount_etb": amount,
                "payment_method": payment_method,
                "category": category,
                "city": city,
                "buyer_id": st.session_state.user_id,
                "seller_id": supplier_id
            }
            
            with st.spinner("🧠 AI is analyzing transaction risk..."):
                result = predict_fraud(transaction)
                
            risk_score = result["risk_score"]
            flags = result["flags"]
            
            # Determine risk level
            if risk_score < 0.3:
                level = "Low"
                color = "green"
            elif risk_score < 0.7:
                level = "Medium"
                color = "orange"
            else:
                level = "High"
                color = "red"
                
            st.markdown(f"### Risk Level: <span style='color:{color}; font-weight:bold;'>{level}</span>", unsafe_allow_html=True)
            st.progress(risk_score)
            st.metric("Risk Score", f"{risk_score * 100:.1f}%")
            
            if flags:
                st.warning("⚠️ Risk Flags Triggered:")
                for flag in flags:
                    st.markdown(f"- {flag}")
            else:
                st.success("✅ No significant risk flags detected.")
