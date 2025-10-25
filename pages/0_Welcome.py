import streamlit as st

# --- Page Configuration ---

# ----- To hide default page show -----
st.markdown("""
    <style>
        [data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

# ---------- Sidebar content Navigation ----------
with st.sidebar:

    st.title("🧠 MindTrack")
    st.markdown("Your personal wellness and habit tracker.")

    # Updated navigation links
    st.page_link("streamlit_app.py", label="Progress Dashboard", icon="📊")
    st.page_link("pages/1_Daily_log.py", label="Daily Log", icon="✏️")
    st.page_link("pages/3_AI_insights.py", label="AI Insights", icon="✨")
    st.page_link("pages/0_Welcome.py", label="About", icon="👋")

# --- Page Configuration ---

st.set_page_config(
    page_title="MindTrack - About",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Welcome Page Content ---
st.title("Welcome to MindTrack! 👋")
st.markdown(
    """
    This is your central hub for building better habits, understanding your moods, 
    and achieving your wellness goals.
    
    Navigate using the sidebar on the left:
    
    - **📊 Progress Dashboard:** Visualize your consistency, track streaks, and see your progress over time.
    - **✍️ Daily Log:** Check in each day to log your habits, mood, and journal entries build a streak to get rewards.
    - **✨ AI Powered:** You write your thoughts, app automatically know how you feel.
    - **✨ AI Insights:** Get new habits suggestions based on your history.
    - **🔥 Share:** Share your hot streaks with your friends.
    
    Let's get started!
    """
)

st.header("How to Use")
st.info(
    """
    1.  Go to the **Daily Log** page to enter your data for the day.
    2.  Visit the **Progress Dashboard** to see your trends.
    3.  Use **AI Insights** to reflect on your journal entries and history.
    """
)
