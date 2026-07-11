import streamlit as st

def render_profile_card(user_data: dict, match_score: int = None):
    """
    Renders a reusable profile card for users.
    user_data: dict with keys like name, role, city, verification_status, rating.
    """
    name = user_data.get("name", "Unknown User")
    role = user_data.get("role", "user").capitalize()
    city = user_data.get("city", "Unknown City")
    is_verified = user_data.get("verification_status") == "verified"
    rating = user_data.get("rating", 0.0)
    
    badge = "✅ Verified" if is_verified else "⚠️ Unverified"
    stars = "⭐" * int(rating) if rating else "No ratings yet"
    
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        col1.markdown(f"### {name}")
        col1.markdown(f"**{role}** | 📍 {city}")
        col1.caption(f"{badge} | {stars}")
        
        if match_score is not None:
            col2.metric("Match Score", f"{match_score}%")
            st.progress(match_score / 100.0)
