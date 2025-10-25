import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, timedelta, date
import calplot
import matplotlib.pyplot as plt
import plotly.express as px
import time
from dotenv import load_dotenv

load_dotenv()


# --- Page Config ---
st.set_page_config(
    page_title="Progress Dashboard",
    page_icon="📊",
    layout="wide",
)

# --- HIDE STREAMLIT'S DEFAULT PAGE NAVIGATION ---
st.markdown("""
    <style>
        [data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Backend/Data URLS ---
BACKEND_URL = os.getenv("BACKEND_URL")
SAMPLE_LOGS_FILE = "data/sample_logs.csv" # The fallback file


# --- Sidebar ---
with st.sidebar:
    st.title("🧠 MindTrack")
    st.markdown("Your personal wellness and habit tracker.")

    # --- Calming Audio Player ---
    # st.audio(
    #     "https://archive.org/download/calm-ambient-piano-loop-14-110-bpm/calm-ambient-piano-loop-14-110-bpm_102bpm.mp3", 
    #     format="audio/mpeg",
    #     start_time=0
    # )
    # st.caption("Calming audio (press play)")

    st.page_link("streamlit_app.py", label="Progress Dashboard", icon="📊")
    st.page_link("pages/1_Daily_log.py", label="Daily Log", icon="✏️")
    st.page_link("pages/3_AI_insights.py", label="AI Insights", icon="✨")
    st.page_link("pages/0_Welcome.py", label="About", icon="👋")

    if st.button("Reset to Sample Data", help="Deletes all user logs from the backend and reloads sample data.", type="secondary"):
        try:
            with st.spinner("Resetting data..."):
                reset_url = f"{BACKEND_URL}/reset_logs"
                response = requests.post(reset_url, timeout=10)
                
                response.raise_for_status() # Raise error if status is 4xx/5xx
                
                st.success("Data reset! Reloading...")
                st.cache_data.clear() # Clear the data cache
                time.sleep(1) # Give a moment for the user to see the message
                st.rerun() # Force a full rerun

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to reset data. Backend may be offline. {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    

# --- Helper Functions ---

def calculate_streaks(active_dates_list):
    """Calculates the current and longest streaks from a list of dates."""
    # We must check the .size of a numpy array
    if active_dates_list.size == 0: 
        return 0, 0

    sorted_dates = sorted(list(set(active_dates_list))) # Ensure unique and sorted
    if not sorted_dates:
        return 0, 0

    # --- Calculate Longest Streak ---
    longest_streak = 0
    current_temp_streak = 1 # Start at 1 for the first date
    
    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] == sorted_dates[i-1] + timedelta(days=1):
            # Streak continues
            current_temp_streak += 1
        else:
            # Streak broken, update longest if needed
            if current_temp_streak > longest_streak:
                longest_streak = current_temp_streak
            current_temp_streak = 1 # Reset for the new date
            
    # Final check after loop
    if current_temp_streak > longest_streak:
        longest_streak = current_temp_streak

    # --- Calculate Current Streak ---
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    current_streak = 0
    
    if today in sorted_dates:
        current_streak = 1
        temp_date = yesterday
        while temp_date in sorted_dates:
            current_streak += 1
            temp_date -= timedelta(days=1)
            
    elif yesterday in sorted_dates:
        # Today not logged, but yesterday was
        current_streak = 1
        temp_date = yesterday - timedelta(days=1)
        while temp_date in sorted_dates:
            current_streak += 1
            temp_date -= timedelta(days=1)
    
    # If neither today nor yesterday is logged, current_streak remains 0
       
    return current_streak, longest_streak



def load_data():
    """
    Tries to load all logs from the backend.
    If it fails, falls back to local sample_logs.csv for demo.
    """
    try:
        # 1. Try to fetch live data from the backend
        response = requests.get(f"{BACKEND_URL}/get_all_logs", timeout=5)
        response.raise_for_status() # Raise an error if the request failed
        
        data = response.json()

        print(f"DATA FROm BACKEND : {data}")
        
        if not data:
            st.toast("No logs found in backend. Loading samples.", icon="ℹ️")
            raise requests.exceptions.RequestException("Empty data")
            
        logs_df = pd.DataFrame(data)
        st.toast("Loaded live data from backend!", icon="✅")
        
    except requests.exceptions.RequestException as e:
        # 2. Fallback to local sample data
        st.toast(f"Backend not reachable: {e}. Loading local sample data for demo.", icon="⚠️")
        try:
            logs_df = pd.read_csv(SAMPLE_LOGS_FILE)
        except FileNotFoundError:
            st.error(f"Sample file not found at {SAMPLE_LOGS_FILE}. Cannot display data.")
            return pd.DataFrame(), 0, 0
    
    # 3. Process data (This happens for both live and sample data)
    try:
        # Keep as full datetime objects for calplot
        logs_df['date'] = pd.to_datetime(logs_df['date']) 
        logs_df = logs_df.drop_duplicates(subset=['date'], keep='last').sort_values(by='date')
        
        # Calculate total_habits for each day
        habits = ["water", "reading", "meditation", "exercise"]
        available_habits = [h for h in habits if h in logs_df.columns]
        
        for habit in available_habits:
             logs_df[habit] = pd.to_numeric(logs_df[habit], errors='coerce').fillna(0)
        logs_df['total_habits'] = logs_df[available_habits].sum(axis=1)

        # Get active dates for streak calculation (as date objects)
        active_dates_as_date = logs_df['date'].dt.date.unique()
        current_s, longest_s = calculate_streaks(active_dates_as_date)
        
        return logs_df, current_s, longest_s # Return DF with full datetime
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return pd.DataFrame(), 0, 0

# --- Load Data ---
logs_df, current_streak, longest_streak = load_data()

APP_URL = os.getenv("APP_URL") 

# ---------- Sharing with friends ---------------------
    
st.sidebar.divider()
st.sidebar.subheader("Share Your Progress")

# Generate the shareable text
share_text = f"""
I'm on a {current_streak}-day streak 
with MindTrack!🔥
#MindTrackApp
Check out the app : {APP_URL}"""  

# Showing text in a code box so it's easy to copy
st.sidebar.code(share_text, language=None)
st.sidebar.caption("Copy the text above to share your progress with friends!")


# --- Daily Motivational Quote ---

def get_daily_quote():
    quotes = [
        "The secret of getting ahead is getting started. - Mark Twain",
        "Your future is created by what you do today, not tomorrow. - Robert Kiyosaki",
        "Well done is better than well said. - Benjamin Franklin",
        "Small progress is still progress. - Unknown",
        "Success is the sum of small efforts, repeated day in and day out. - Robert Collier",
        "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
        "The only way to do great work is to love what you do. - Steve Jobs"
    ]
    # Use the day of the year to pick a quote
    day_of_year = date.today().timetuple().tm_yday
    return quotes[day_of_year % len(quotes)]

st.success(f"Quote of the Day : {get_daily_quote()}", icon="💡")


# --- Streak Reward Logic ---
if 'last_celebrated_streak' not in st.session_state:
    st.session_state.last_celebrated_streak = 0
if 'show_reward_dialogue' not in st.session_state: # Add new state for dialog
    st.session_state.show_reward_dialogue = False
if 'milestone_achieved' not in st.session_state: # Store the milestone
    st.session_state.milestone_achieved = 0


# Reset celebration if streak is broken
if current_streak == 0:
     st.session_state.last_celebrated_streak = 0

# Check for milestones (e.g., 3, 5, 7 days)
milestone = 0
if current_streak == 3:
    milestone = 3
elif current_streak == 5:
    milestone = 5
elif current_streak == 7:
    milestone = 7
elif current_streak == 21:
    milestone = 21
elif current_streak == 30:
    milestone = 30
elif current_streak == 60:
    milestone = 60

# If we hit a new milestone that we haven't celebrated, app shows balloons!
if milestone > 0 and st.session_state.last_celebrated_streak < milestone:
    st.balloons()
    st.success(f"Congrats on your {milestone}-day streak! 🎉 Keep it up!", icon="🔥")
    st.session_state.last_celebrated_streak = milestone
# --- END Streak Reward Logic ---



# --- Streak Reward Dialog ---
if st.session_state.get("show_reward_dialogue", False):
    @st.dialog("Streak Milestone Reached! 🔥")
    def show_reward_dialog():
        milestone = st.session_state.get("milestone_achieved", 0)
        st.success(f"Congrats on your {milestone}-day streak! 🎉 Keep it up!", icon="🔥")
        st.balloons()
        if st.button("Awesome!", type="primary", use_container_width=True):
            st.session_state.show_reward_dialog = False
            st.rerun()
    
    show_reward_dialog() # This calls the dialog function to open it
# --- END Streak Reward Dialog ---



# --- Main Page ---
st.title("📊 Progress Dashboard")

if logs_df.empty:
    st.info("No data to display. Start by adding an entry in the 'Daily Log' page!")
else:
    # --- Key Metrics ---
    st.subheader("Your Streaks")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Days Logged", f"{len(logs_df)}")
    col2.metric("Current Streak", f"{current_streak} 🔥")
    col3.metric("Longest Streak", f"{longest_streak} 🏆")

    st.divider()

    # --- Habit Calendar Heatmap ---
    st.subheader("Habit Calendar")
    
    try:
        # Data is already prepared with 'total_habits' and DatetimeIndex in load_data
        heatmap_data = logs_df.set_index('date')['total_habits'].astype(float)
        
        max_habits = 4 # Assuming 4 habits

        plt.style.use('dark_background')
        
        # Clear any existing plots from matplotlib's state
        plt.clf()

        # Let calplot create its own figure and axes
        calplot.calplot(
            heatmap_data,
            cmap='YlGn',
            edgecolor='black',
            fillcolor='gray',
            linewidth=0.5,
            yearlabels=True,
            yearascending=True,
            figsize=(12, 5),
            textformat='{:.0f}',
            vmin=0,
            vmax=4,
            colorbar=False
        )
        
        # Using st.pyplot(plt.gcf()) to grab the current figure
        st.pyplot(plt.gcf()) 
        
        st.caption(f"Color intensity shows total habits completed (0 to {max_habits}).")

    except Exception as e:
        st.error(f"Error generating calendar plot: {e}")

    st.divider()

    # --- Daily Progress Trend (Line Chart) ---
    st.subheader("Daily Progress Trend")
    try:
        fig_line = px.line(
            logs_df.sort_values(by='date'),
            x='date',
            y='total_habits',
            title="Total Habits Completed Over Time",
            markers=True,
            template='plotly_dark' # Using dark theme
        )
        fig_line.update_layout(xaxis_title="Date", yaxis_title="Habits Completed")
        st.plotly_chart(fig_line, use_container_width=True)
    except Exception as e:
        st.error(f"Error generating trend line: {e}")

    st.divider()

    # --- Other Visualizations Bar & Pie---
    st.subheader("Habit & Mood Analysis")
    
    c1, c2 = st.columns(2)
    
    
    with c1:
        # 1. Habit Completion Rate (Bar Chart)
        st.markdown("##### Habit Completion Rate")
        habits = ['exercise', 'water', 'reading', 'meditation']
        # Filter for habits that actually exist
        available_habits = [h for h in habits if h in logs_df.columns]
        
        habit_counts = logs_df[available_habits].sum()
        habit_df = habit_counts.reset_index()
        habit_df.columns = ['Habit', 'Days Completed']
        
        fig_bar = px.bar(
            habit_df, 
            template='seaborn',
            x='Habit', 
            y='Days Completed', 
            color='Habit',
            title="Total Times Each Habit Was Completed"
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c2:
        # 2. Mood Distribution (Pie Chart)
        st.markdown("##### AI Logged Mood Distribution")
        mood_counts = logs_df['mood'].value_counts().reset_index()
        mood_counts.columns = ['Mood', 'Count']
        
        fig_pie = px.pie(
            mood_counts, 
            template='seaborn',
            names='Mood', 
            values='Count',
            title="Moods Recorded by AI Analysis",
            hole=0.3
        )
        st.plotly_chart(fig_pie, use_container_width=True)

