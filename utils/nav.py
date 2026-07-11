import streamlit as st

def render_sidebar():
    """Renders the role-specific sidebar navigation using session state."""
    role = st.session_state.get("role")
    if not role:
        return

    st.sidebar.title("EthioChain")
    st.sidebar.markdown(f"**{st.session_state.get('name', 'User')}** ({role.capitalize()})")
    st.sidebar.markdown("---")

    # Define navigation options per role
    nav_map = {
        "producer": ["Dashboard", "Inventory", "Find Merchants"],
        "merchant": ["Dashboard", "Marketplace", "Find Producers", "Fraud Check"],
        "customer": ["Home", "Marketplace", "For You", "Favorites"],
        "admin": ["Dashboard", "Users", "Products", "Fraud Alerts", "AI Models", "Settings", "Reports"]
    }

    options = nav_map.get(role, [])
    
    # Initialize session state for tab if not set
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = options[0]
        
    # Radio button for navigation
    selected = st.sidebar.radio(
        "Navigation", 
        options, 
        index=options.index(st.session_state.current_tab) if st.session_state.current_tab in options else 0
    )
    
    # Rerun if tab changed
    if selected != st.session_state.current_tab:
        st.session_state.current_tab = selected
        st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        from utils.auth import logout
        logout()
