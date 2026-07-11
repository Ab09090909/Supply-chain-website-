import streamlit as st
import pickle
import os
import numpy as np

@st.cache_resource
def _load_recommendation_model():
    path = "models/recommendation_model.pkl"
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception:
            return None
    return None

def get_recommendations(customer_id: str, purchase_history: list, all_available_products: list) -> list:
    """
    Recommends products for a customer.
    all_available_products: List of product IDs currently active in the marketplace.
    Returns: Ranked list of recommended product IDs.
    """
    model = _load_recommendation_model()
    
    # Filter out already purchased items
    available = [p for p in all_available_products if p not in purchase_history]
    
    if model and len(purchase_history) > 0:
        try:
            # Mock feature: number of past purchases
            features = np.array([[len(purchase_history)]])
            # Assume model returns scores for all available products
            # In reality, this would be a matrix factorization or neural collaborative filtering output
            scores = model.predict(features)[0] 
            
            # Map scores to available products (mock mapping)
            product_scores = {p: scores[i % len(scores)] for i, p in enumerate(available)}
            sorted_products = sorted(product_scores, key=product_scores.get, reverse=True)
            return sorted_products[:10]
        except Exception:
            pass
            
    # Fallback: Randomized recommendations from available pool
    np.random.shuffle(available)
    return available[:10]
