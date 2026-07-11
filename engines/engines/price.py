import streamlit as st
import numpy as np

def recommend_price(product_name: str, category: str, sector: str, quantity: float, city: str) -> dict:
    """
    Recommends a price for a product.
    Returns: {"recommended_price_etb": float, "market_range_etb": tuple, "trend": str}
    """
    # Base prices by category in ETB (Rule-based fallback/core logic)
    base_prices = {
        "Grains": 2500, "Vegetables": 1200, "Fruits": 1500, "Livestock": 25000,
        "Building Materials": 8000, "Fabrics": 3000, "Machinery": 150000, 
        "Medicines": 5000, "Consumer Goods": 1500
    }
    
    base = base_prices.get(category, 2000)
    
    # City multiplier (Addis Ababa typically has higher overhead/prices)
    city_mult = {"Addis Ababa": 1.15, "Dire Dawa": 1.05, "Mekelle": 0.95, "Bahir Dar": 1.0}.get(city, 1.0)
    
    # Wholesale/Quantity discount
    qty_mult = 1.0
    if quantity > 100: qty_mult = 0.95
    if quantity > 1000: qty_mult = 0.90
    
    recommended_price = base * city_mult * qty_mult
    
    # Market average range (±10%)
    lower = recommended_price * 0.90
    upper = recommended_price * 1.10
    
    # Mock trend logic (In production, this would query historical price data)
    trend = "stable" 
    if category in ["Building Materials", "Machinery"]:
        trend = "rising"
    elif category in ["Textiles", "Consumer Goods"]:
        trend = "falling"
        
    return {
        "recommended_price_etb": round(recommended_price, 2),
        "market_range_etb": (round(lower, 2), round(upper, 2)),
        "trend": trend
    }
