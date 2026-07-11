import streamlit as st
import pickle
import os
import numpy as np

@st.cache_resource
def _load_fraud_model():
    """Loads the fraud detection model. Caches to prevent reloading on every run."""
    path = "models/fraud_model.pkl"
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.warning(f"Fraud model failed to load: {e}. Using rule-based fallback.")
    return None

def predict_fraud(transaction: dict) -> dict:
    """
    Evaluates a transaction for fraud risk.
    transaction: {"amount_etb": float, "buyer_id": str, "seller_id": str, 
                  "category": str, "payment_method": str, "city": str}
    Returns: {"risk_score": float (0-1), "flags": list of str}
    """
    model = _load_fraud_model()
    flags = []
    
    amount = transaction.get("amount_etb", 0)
    payment_method = transaction.get("payment_method", "")
    
    # --- Rule-Based Feature Extraction ---
    if amount > 500000:
        flags.append("Extremely high transaction amount (>500k ETB)")
    elif amount > 100000:
        flags.append("High transaction amount (>100k ETB)")
        
    valid_methods = ["Telebirr", "CBE Birr", "Dashen Bank", "Amole"]
    if payment_method not in valid_methods:
        flags.append("Unrecognized or unsupported payment method")
        
    # --- Model Inference ---
    if model:
        try:
            # Note: In production, map transaction dict to the exact feature vector the model expects
            features = np.array([[amount, 1 if payment_method == "Telebirr" else 0]])
            risk_score = float(model.predict_proba(features)[0][1])
        except Exception:
            # Fallback if model inference fails
            risk_score = min(len(flags) * 0.4, 1.0)
    else:
        # Pure rule-based fallback score
        risk_score = min(len(flags) * 0.4, 1.0)
        
    return {
        "risk_score": round(risk_score, 3),
        "flags": flags
    }
