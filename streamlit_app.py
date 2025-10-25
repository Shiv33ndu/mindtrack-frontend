import streamlit as st
import pandas as pd
import altair as alt
import requests
import os
import datetime
# We will use calplot and matplotlib for the calendar heatmap
try:
    import calplot
    import matplotlib.pyplot as plt
    CALPLOT_INSTALLED = True
except ImportError:
    CALPLOT_INSTALLED = False

# ----- To hide default page show -----
st.markdown("""
    <style>
        [data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Page Configuration ---

st.set_page_config(
    page_title="MindTrack - Progress Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Configuration ---
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")
SUMMARY_ENDPOINT = f"{BACKEND_URL}/summary"
LOCAL_LOG_FILE = "data/logs.csv"
SAMPLE_LOG_FILE = "data/sample_logs.csv"

# --- Sidebar Navigation ---
with st.sidebar:

    st.title("🧠 MindTrack")
    st.markdown("Your personal wellness and habit tracker.")

    # Updated navigation links
    st.page_link("streamlit_app.py", label="Progress Dashboard", icon="📊")
    st.page_link("pages/1_Daily_Log.py", label="Daily Log", icon="✍️")
    st.page_link("pages/3_AI_Insights.py", label="AI Insights", icon="✨")
    st.page_link("pages/0_Welcome.py", label="About", icon="🏠") # New welcome page



# Daily motivational quote
quotes = [
    "The secret of getting ahead is getting started. - Mark Twain",
    "Your future is created by what you do today, not tomorrow. - Robert Kiyosaki",
    "Well done is better than well said. - Benjamin Franklin",
    "Small progress is still progress. - Unknown",
    "Success is the sum of small efforts, repeated day in and day out. - Robert Collier",
    "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
    "The only way to do great work is to love what you do. - Steve Jobs"
]

today = datetime.date.today()
quote_index = today.day % len(quotes) # Simple way to get a new quote daily


# --- Helper Functions ---

def calculate_streaks(active_dates_list):
    """Calculates the current and longest streaks from a list of active dates."""
    if active_dates_list.size == 0:
        return 0, 0  # current_streak, longest_streak

    # Ensure dates are datetime.date objects and are sorted/unique
    sorted_dates = sorted(active_dates_list)

    if not sorted_dates:
         return 0, 0

    longest_streak = 0
    current_streak_temp = 1
    longest_streak = 1
    
    for i in range(1, len(sorted_dates)):
        delta = sorted_dates[i] - sorted_dates[i-1]
        if delta.days == 1:
            current_streak_temp += 1
        else:
            # Streak is broken
            current_streak_temp = 1
        
        longest_streak = max(longest_streak, current_streak_temp)
    
    # Now check if the last streak is "current"
    today = datetime.date.today()
    last_active_date = sorted_dates[-1]
    
    days_since_last = (today - last_active_date).days
    
    current_streak = 0
    if days_since_last <= 1:
        current_streak = current_streak_temp
    else:
        current_streak = 0 # The streak is broken
        
    return current_streak, longest_streak


# @st.cache_data(ttl=300) # Cache for 5 minutes
def load_data():
    """Fetches summary data from backend or falls back to local CSVs."""
    try:
        response = requests.get(SUMMARY_ENDPOINT, timeout=5) # Added timeout
        if response.status_code == 200:
            st.toast("Data loaded from backend.")
            data = response.json()
            # Convert date strings to datetime objects
            logs_df = pd.DataFrame(data["logs"])
            if not logs_df.empty:
                logs_df['date'] = pd.to_datetime(logs_df['date'])
            return data["summary"], logs_df
    except requests.exceptions.ConnectionError:
        st.warning("Backend not reachable. Loading local data (if any).")
    except requests.exceptions.Timeout:
        st.warning("Backend connection timed out. Loading local data.")
    
    # Fallback to local files
    df_local = pd.DataFrame()
    df_sample = pd.DataFrame()

    try:
        if os.path.exists(LOCAL_LOG_FILE):
            df_local = pd.read_csv(LOCAL_LOG_FILE)
        
        if os.path.exists(SAMPLE_LOG_FILE):
            df_sample = pd.read_csv(SAMPLE_LOG_FILE)
    except pd.errors.EmptyDataError:
        pass # It's okay if the local log file is empty
    except Exception as e:
        st.error(f"Error loading local data: {e}")
        return {}, pd.DataFrame(columns=['date'])


    if df_local.empty and df_sample.empty:
        st.error("No data found. Please make some entries in the Daily Log.")
        return {}, pd.DataFrame(columns=['date'])

    # Combine local and sample data
    logs_df = pd.concat([df_sample, df_local]).drop_duplicates(subset=['date'], keep='last').sort_values(by='date')
    
    if not logs_df.empty:
        logs_df['date'] = pd.to_datetime(logs_df['date'])

        # --- START NEW STREAK LOGIC ---
        # We must calculate total_habits here to find streaks
        habits = ["water", "reading", "meditation", "exercise"]
        available_habits = [h for h in habits if h in logs_df.columns]
        for habit in available_habits:
            logs_df[habit] = pd.to_numeric(logs_df[habit], errors='coerce').fillna(0)
        
        if available_habits:
            logs_df['total_habits'] = logs_df[available_habits].sum(axis=1)
        else:
            logs_df['total_habits'] = 0

        # Filter for active days (at least one habit)
        active_days_df = logs_df[logs_df['total_habits'] > 0]
        # Get a list of unique datetime.date objects
        active_dates_list = active_days_df['date'].dt.date.unique()

        print(f"Active : {active_dates_list}")
        
        current_s, longest_s = calculate_streaks(active_dates_list)
        # --- END NEW STREAK LOGIC ---

        # Simple summary calculation for fallback
        summary = {
            "total_logs": len(logs_df),
            "current_streak": current_s,
            "longest_streak": longest_s,
        }
        st.toast("Displaying local/sample data.")
        return summary, logs_df
    
    return {}, pd.DataFrame(columns=['date'])

# --- Page UI ---
st.title("📊 Progress Dashboard")
# st.markdown("Visualize your consistency and track your progress.")

st.success(f"💡{quotes[quote_index]}")

summary_data, logs_df = load_data()

if not logs_df.empty:
    # --- Key Metrics ---
    st.header("Your At-a-Glance Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Days Logged", summary_data.get("total_logs", "N/A"))
    col2.metric("Current Streak", f"{summary_data.get('current_streak', 'N/A')} 🔥")
    col3.metric("Longest Streak", f"{summary_data.get('longest_streak', 'N/A')} 🏆")
    
    st.divider()

    # --- Habits Over Time Chart ---
    st.header("Habit Completion Calendar")
    
    # UPDATED habit list to match new CSV
    habits = ["water", "reading", "meditation", "exercise"]
    
    # Filter for habits that actually exist in the dataframe
    available_habits = [h for h in habits if h in logs_df.columns]
    
    if not available_habits:
        st.warning("Habit columns (water, reading, meditation, exercise) not found in data.")
    else:
        # --- THIS IS THE NEW LOGIC ---
        # 1. Calculate total habits completed per day
        # Ensure habit columns are numeric before summing
        # This is now done in load_data, but we ensure 'total_habits' exists
        if 'total_habits' not in logs_df.columns:
            st.warning("Recalculating habits. This should be done in load_data.")
            for habit in available_habits:
                 logs_df[habit] = pd.to_numeric(logs_df[habit], errors='coerce').fillna(0)
            logs_df['total_habits'] = logs_df[available_habits].sum(axis=1)
        
        max_habits = len(available_habits)

        # 2. Prepare data for the heatmap component
        # It needs a pandas Series with a DatetimeIndex and int values
        # Ensure data type is correct for calplot
        heatmap_data = logs_df.set_index('date')['total_habits'].astype(float)
        
        # 3. Display the calendar heatmap
        st.markdown("##### Daily Habit Completion")
        
        plt.style.use('dark_background')

        if CALPLOT_INSTALLED:
            try:
                # --- MODIFIED SECTION ---
                
                # Clear any existing plots from matplotlib's state
                plt.clf()

                # Let calplot create its own figure and axes
                # We don't pass fig or ax
                calplot.calplot(
                    heatmap_data,
                    cmap='YlGn',
                    edgecolor='black',
                    # linecolor='gray',
                    fillcolor='gray',
                    linewidth=0.5,
                    yearlabels=True,
                    yearascending=True,
                    figsize=(12, 5), # We can suggest a size here
                    textformat='{:.0f}'
                )
                
                # Use st.pyplot() with no arguments, or st.pyplot(plt.gcf())
                # This tells Streamlit to grab the "current figure"
                st.pyplot(plt.gcf()) 
                
                # --- END MODIFIED SECTION ---

                st.caption(f"Color intensity shows total habits completed (0 to {max_habits}).")
            except Exception as e:
                st.error(f"Error generating calendar plot: {e}")
                st.write("Please ensure your data is correctly formatted.")
        else:
            st.error("Missing libraries for calendar view.")
            st.code("pip install calplot matplotlib")
            st.markdown(
                "Please add `calplot` and `matplotlib` to your `requirements.txt` file and restart."
            )


    st.divider()

    # --- Mood Distribution ---
    st.header("Mood Distribution")
    if "mood" in logs_df.columns:
        mood_counts = logs_df["mood"].value_counts().reset_index()
        mood_counts.columns = ["Mood", "Count"]

        pie_chart = alt.Chart(mood_counts).mark_arc(outerRadius=120).encode(
            theta=alt.Theta("Count", stack=True),
            color=alt.Color("Mood", legend=alt.Legend(title="Mood")),
            tooltip=["Mood", "Count"]
        ).properties(
            title="Your Moods at a Glance"
        )
        st.altair_chart(pie_chart, use_container_width=True)
    else:
        st.info("No mood data logged yet.")

else:
    st.info("No data to display. Go to the 'Daily Log' page to start tracking!")

