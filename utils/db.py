import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_supabase() -> Client:
    """
    Initializes and caches the Supabase client.
    Uses Streamlit secrets for credentials. Never uses .env or os.getenv.
    """
    try:
        url: str = st.secrets["SUPABASE_URL"]
        key: str = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError as e:
        st.error(f"Missing Supabase secret: {e}. Please check your Streamlit Cloud secrets.")
        st.stop()

# Single client instance to be imported everywhere
supabase: Client = init_supabase()
