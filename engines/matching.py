import streamlit as st
import pickle
import os
import numpy as np

# Ethiopian Sector and Region Encoding Maps
SECTOR_MAP = {
    "Agriculture": 0, "Manufacturing": 1, "Construction": 2, 
    "Textiles": 3, "Electronics": 4, "Pharmaceuticals": 5
}
CITY_MAP = {
    "Addis Ababa": 0, "Dire Dawa": 1, "Mekelle": 2, "Gondar": 3, 
    "Bahir Dar": 4, "Hawassa": 5, "Adama": 6, "Jimma": 7
}

@st.cache_resource
def _load_matching_model():
    path = "models/matching_model.pkl"
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception:
            return None
    return None

def find_matches(user_profile: dict, product_context: dict, counterparties: list) -> list:
    """
    Matches a user with counterparties (producers or merchants).
    counterparties: List of dicts with keys like 'id', 'name', 'city', 'sector'.
    Returns: Sorted list of counterparties with an added 'match_score' (0-100).
    """
    model = _load_matching_model()
    
    user_city = user_profile.get("city", "Addis Ababa")
    user_sector = product_context.get("sector", "Agriculture")
    
    if model:
        try:
            # Mock feature extraction for the ML model
            features = np.array([[
                SECTOR_MAP.get(user_sector, 0), 
                CITY_MAP.get(user_city, 0)
            ]])
            # Assume model returns similarity scores
            scores = model.predict(features)[0] 
            for i, cp in enumerate(counterparties):
                cp["match_score"] = int((scores[i % len(scores)] + 1) * 50) # Normalize to 0-100
        except Exception:
            _apply_rule_based_scores(counterparties, user_city, user_sector)
    else:
        _apply_rule_based_scores(counterparties, user_city, user_sector)
            
    return sorted(counterparties, key=lambda x: x["match_score"], reverse=True)

def _apply_rule_based_scores(counterparties: list, user_city: str, user_sector: str):
    """Fallback scoring based on exact matches in city and sector."""
    for cp in counterparties:
        score = 50 # Base score
        if cp.get("city") == user_city:
            score += 25
        if cp.get("sector") == user_sector:
            score += 25
        cp["match_score"] = min(score, 100)
