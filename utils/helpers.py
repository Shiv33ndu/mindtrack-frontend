import streamlit as st
from PIL import Image

# This helper is minimal for now.
# You can add more functions here, e.g., for data processing or API calls.

@st.cache_data
def load_assets():
    """
    Loads and caches image assets.
    NOTE: This path is relative to the root of the streamlit app.
    This might not work well with multi-page apps depending on structure.
    Using emojis is often more reliable for hackathons.
    """
    try:
        water_icon = Image.open("assets/icons/water.png")
        read_icon = Image.open("assets/icons/read.png")
        meditate_icon = Image.open("assets/icons/meditate.png")
        return water_icon, read_icon, meditate_icon
    except FileNotFoundError:
        st.error("Icon files not found. Please make sure `assets/icons/` folder exists.")
        return None, None, None

def get_backend_url():
    """
    Placeholder for a more robust URL management.
    In a real app, you'd use environment variables.
    """
    # For local development
    return "http://127.0.0.1:5000"
    # For deployed app
    # return "https...your-render-app-url.onrender.com"
