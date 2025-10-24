import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Welcome - MindTrack",
    page_icon="🏠",
)

# --- Welcome Page Content ---
st.title("Welcome to MindTrack! 👋")
st.markdown(
    """
    This is your central hub for building better habits, understanding your moods, 
    and achieving your wellness goals.
    
    Navigate using the sidebar on the left:
    
    - **📊 Progress Dashboard:** Visualize your consistency, track streaks, and see your progress over time.
    - **✍️ Daily Log:** Check in each day to log your habits, mood, and journal entries.
    - **✨ AI Insights:** Get a sentiment analysis of your journal entries and a motivational boost.
    
    Let's get started!
    """
)

st.header("How to Use")
st.info(
    """
    1.  Go to the **Daily Log** page to enter your data for the day.
    2.  Visit the **Progress Dashboard** to see your trends.
    3.  Use **AI Insights** to reflect on your journal entries.
    """
)
