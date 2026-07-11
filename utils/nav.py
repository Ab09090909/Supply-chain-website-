import streamlit as st

def render_sidebar():
    """Renders the role-specific sidebar navigation."""
    role = st.session_state.get("role")
    if not role:
        return

    st.sidebar.title("EthioChain")
    st.sidebar.markdown(f"**{st.session_state.get('name', 'User')}** ({role.capitalize()})")
    st.sidebar.markdown("---")

    # Define navigation options and their corresponding page paths
    nav_map = {
        "producer": {
            "Dashboard": "pages/1_producer.py",
            "Inventory": "producer/inventory.py",
            "Find Merchants": "producer/merchant_matching.py"
        },
        "merchant": {
            "Dashboard": "pages/2_merchant.py",
            "Marketplace": "merchant/marketplace.py",
            "Find Producers": "merchant/producer_matching.py",
            "Fraud Check": "merchant/fraud_check.py"
        },
        "customer": {
            "Home": "pages/3_customer.py",
            "Marketplace": "customer/marketplace.py",
            "For You": "customer/recommendations.py",
            "Favorites": "customer/favorites.py"
        },
        "admin": {
            "Admin Dashboard": "pages/4_admin.py",
            "Users": "admin/user_management.py",
            "Products": "admin/product_management.py",
            "Fraud Alerts": "admin/fraud_monitoring.py",
            "AI Models": "admin/ml_performance.py",
            "Settings": "admin/system_settings.py",
            "Reports": "admin/reports.py"
        }
    }

    options = list(nav_map.get(role, {}).keys())
    selected = st.sidebar.radio("Navigation", options)
    
    if selected:
        target_page = nav_map[role][selected]
        if st.sidebar.button(f"Go to {selected}", use_container_width=True):
            st.switch_page(target_page)

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        from utils.auth import logout
        logout()
