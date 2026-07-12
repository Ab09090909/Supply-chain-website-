import streamlit as st

def render_sidebar():
    """Renders the role-specific sidebar navigation using session state."""
    role = st.session_state.get("role")
    if not role:
        return

    st.sidebar.title("EthioChain")
    st.sidebar.markdown(f"**{st.session_state.get('name', 'User')}** ({role.capitalize()})")
    st.sidebar.markdown("---")

    # Added "AI Assistant" to every role's tab list
    nav_map = {
        "producer": ["Dashboard", "Inventory", "Find Merchants", "AI Assistant"],
        "merchant": ["Dashboard", "Marketplace", "Find Producers", "Fraud Check", "AI Assistant"],
        "customer": ["Home", "Marketplace", "For You", "Favorites", "AI Assistant"],
        "admin": ["Dashboard", "Users", "Products", "Fraud Alerts", "AI Models", "Settings", "Reports", "AI Assistant"]
    }

    options = nav_map.get(role, [])
    
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = options[0]
        
    selected = st.sidebar.radio(
        "Navigation", 
        options, 
        index=options.index(st.session_state.current_tab) if st.session_state.current_tab in options else 0
    )
    
    if selected != st.session_state.current_tab:
        st.session_state.current_tab = selected
        st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        from utils.auth import logout
        logout()
