import streamlit as st

def render_sidebar():
    """Renders the role-specific sidebar navigation using session state."""
    role = st.session_state.get("role")
    if not role:
        return

    st.sidebar.title("EthioChain")
    st.sidebar.markdown(f"**{st.session_state.get('name', 'User')}** ({role.capitalize()})")
    st.sidebar.markdown("---")

    nav_map = {
        "producer": ["Dashboard", "Inventory", "Find Merchants"],
        "merchant": ["Dashboard", "Marketplace", "Find Producers", "Fraud Check"],
        "customer": ["Home", "Marketplace", "For You", "Favorites"],
        "admin": ["Dashboard", "Users", "Products", "Fraud Alerts", "AI Models", "Settings", "Reports"]
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

def render_global_search_bar():
    """Renders the floating pill-shaped search bar at the top of every page."""
    st.markdown("""
    <style>
    /* Floating Container */
    .global-search-container {
        position: fixed;
        top: 15px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 600px;
        z-index: 9999;
    }
    /* The Pill Shape */
    .search-pill {
        background-color: #2a2d36; /* Dark gray matching your image */
        border-radius: 50px;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        border: 1px solid #3a3d46;
    }
    /* Icons */
    .search-icon, .mic-icon {
        color: #a0a0a0;
        display: flex;
        align-items: center;
    }
    /* Input Field */
    .search-input {
        background: transparent;
        border: none;
        color: white;
        flex-grow: 1;
        margin: 0 15px;
        font-size: 16px;
        outline: none;
    }
    .search-input::placeholder {
        color: #a0a0a0;
    }
    /* Push main content down so the floating bar doesn't cover it */
    .block-container {
        padding-top: 80px !important;
    }
    </style>
    
    <div class="global-search-container">
        <div class="search-pill">
            <div class="search-icon">
                <!-- Magnifying Glass SVG -->
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </div>
            <input type="text" class="search-input" placeholder="Search">
            <div class="mic-icon">
                <!-- Microphone SVG -->
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
