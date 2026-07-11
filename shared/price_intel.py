import streamlit as st
from engines.price import recommend_price
from utils.constants import format_etb

def render_price_intel(product_name: str, category: str, sector: str, quantity: float, city: str):
    """
    Displays AI price recommendations and market intelligence.
    """
    st.subheader("💰 Price Intelligence")
    
    try:
        intel = recommend_price(product_name, category, sector, quantity, city)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Recommended Price", format_etb(intel["recommended_price_etb"]))
        col2.metric("Market Range", f"{format_etb(intel['market_range_etb'][0])} - {format_etb(intel['market_range_etb'][1])}")
        
        trend_icon = "📈" if intel["trend"] == "rising" else "📉" if intel["trend"] == "falling" else "➡️"
        col3.metric("Market Trend", f"{trend_icon} {intel['trend'].capitalize()}")
        
    except Exception as e:
        st.error(f"Failed to fetch price intelligence: {str(e)}")
