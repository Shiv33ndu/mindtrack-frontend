# import streamlit as st
# from utils.helpers import load_assets

# # --- Page Configuration ---
# # Must be the first Streamlit command
# st.set_page_config(
#     page_title="MindTrack - Personal Wellness Tracker",
#     page_icon="🧠",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # --- Asset Loading ---
# # We'll use emojis as placeholders since local assets can be tricky in deployment
# # If you deploy and add your assets/, you can uncomment the lines below.
# # water_icon, read_icon, meditate_icon = load_assets()

# # --- Sidebar Navigation ---
# st.sidebar.title("🧠 MindTrack")
# st.sidebar.markdown("Your personal wellness and habit tracker.")

# st.sidebar.page_link("streamlit_app.py", label="Welcome", icon="🏠")
# st.sidebar.page_link("pages/1_Daily_Log.py", label="Daily Log", icon="✍️")
# st.sidebar.page_link("pages/2_Progress_Dashboard.py", label="Progress Dashboard", icon="📊")
# st.sidebar.page_link("pages/3_AI_Insights.py", label="AI Insights", icon="✨")


# # --- Welcome Page Content ---
# st.title("Welcome to MindTrack! 👋")
# st.markdown(
#     """
#     This is your central hub for building better habits, understanding your moods, 
#     and achieving your wellness goals.
    
#     Navigate using the sidebar on the left:
    
#     - **✍️ Daily Log:** Check in each day to log your habits, mood, and journal entries.
#     - **📊 Progress Dashboard:** Visualize your consistency, track streaks, and see your progress over time.
#     - **✨ AI Insights:** Get a sentiment analysis of your journal entries and a motivational boost.
    
#     Let's get started!
#     """
# )

# st.header("How to Use")
# st.info(
#     """
#     1.  Go to the **Daily Log** page to enter your data for the day.
#     2.  Visit the **Progress Dashboard** to see your trends.
#     3.  Use **AI Insights** to reflect on your journal entries.
#     """
# )




# import streamlit as st
# import pandas as pd
# import altair as alt
# import requests
# import os
# import datetime

# # --- Page Configuration ---
# # Must be the first Streamlit command
# st.set_page_config(
#     page_title="MindTrack - Progress Dashboard",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # --- Configuration ---
# BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")
# SUMMARY_ENDPOINT = f"{BACKEND_URL}/summary"
# LOCAL_LOG_FILE = "data/logs.csv"
# SAMPLE_LOG_FILE = "data/sample_logs.csv"

# # --- Sidebar Navigation ---
# st.sidebar.title("🧠 MindTrack")
# st.sidebar.markdown("Your personal wellness and habit tracker.")

# # Updated navigation links
# st.sidebar.page_link("streamlit_app.py", label="Progress Dashboard", icon="📊")
# st.sidebar.page_link("pages/1_Daily_Log.py", label="Daily Log", icon="✍️")
# st.sidebar.page_link("pages/3_AI_Insights.py", label="AI Insights", icon="✨")
# st.sidebar.page_link("pages/0_Welcome.py", label="Welcome", icon="🏠") # New welcome page

# st.sidebar.info(
#     """
#     This app was built for a 2-day hackathon. 
#     Track your habits, mood, and get AI-powered insights.
#     """
# )

# # --- Helper Functions ---
# @st.cache_data(ttl=300) # Cache for 5 minutes
# def load_data():
#     """Fetches summary data from backend or falls back to local CSVs."""
#     try:
#         response = requests.get(SUMMARY_ENDPOINT)
#         if response.status_code == 200:
#             st.toast("Data loaded from backend.")
#             data = response.json()
#             # Convert date strings to datetime objects
#             logs_df = pd.DataFrame(data["logs"])
#             if not logs_df.empty:
#                 logs_df['date'] = pd.to_datetime(logs_df['date'])
#             return data["summary"], logs_df
#     except requests.exceptions.ConnectionError:
#         st.warning("Backend not reachable. Loading local data (if any).")
    
#     # Fallback to local files
#     df_local = pd.DataFrame()
#     df_sample = pd.DataFrame()

#     try:
#         if os.path.exists(LOCAL_LOG_FILE):
#             df_local = pd.read_csv(LOCAL_LOG_FILE)
        
#         if os.path.exists(SAMPLE_LOG_FILE):
#             df_sample = pd.read_csv(SAMPLE_LOG_FILE)
#     except pd.errors.EmptyDataError:
#         pass # It's okay if the local log file is empty
#     except Exception as e:
#         st.error(f"Error loading local data: {e}")
#         return {}, pd.DataFrame(columns=['date'])


#     if df_local.empty and df_sample.empty:
#         st.error("No data found. Please make some entries in the Daily Log.")
#         return {}, pd.DataFrame(columns=['date'])

#     # Combine local and sample data
#     logs_df = pd.concat([df_sample, df_local]).drop_duplicates(subset=['date'], keep='last')
    
#     if not logs_df.empty:
#         logs_df['date'] = pd.to_datetime(logs_df['date'])
#         # Simple summary calculation for fallback
#         summary = {
#             "total_logs": len(logs_df),
#             "current_streak": 0, # Simple fallback
#             "longest_streak": 0, # Simple fallback
#         }
#         st.toast("Displaying local/sample data.")
#         return summary, logs_df
    
#     return {}, pd.DataFrame(columns=['date'])

# # --- Page UI ---
# st.title("📊 Progress Dashboard")
# st.markdown("Visualize your consistency and track your progress.")

# summary_data, logs_df = load_data()

# if not logs_df.empty:
#     # --- Key Metrics ---
#     st.header("Your At-a-Glance Stats")
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Total Days Logged", summary_data.get("total_logs", "N/A"))
#     col2.metric("Current Streak", f"{summary_data.get('current_streak', 'N/A')} 🔥")
#     col3.metric("Longest Streak", f"{summary_data.get('longest_streak', 'N/A')} 🏆")
    
#     st.divider()

#     # --- Habits Over Time Chart ---
#     st.header("Habit Completion Over Time")
    
#     # Melt dataframe for Altair
#     # UPDATED habit list to match new CSV
#     habits = ["water", "reading", "meditate", "exercise"]
    
#     # Filter for habits that actually exist in the dataframe
#     available_habits = [h for h in habits if h in logs_df.columns]
    
#     if not available_habits:
#         st.warning("Habit columns (water, reading, meditate, exercise) not found in data.")
#     else:
#         df_melted = logs_df.melt(id_vars=["date"], value_vars=available_habits, var_name="Habit", value_name="Completed")
        
#         # Ensure 'Completed' is numeric (1 for 1, 0 for 0)
#         df_melted["Completed_Num"] = pd.to_numeric(df_melted["Completed"], errors='coerce').fillna(0).astype(int)

#         # Create the heatmap (Calendar View)
#         heatmap = alt.Chart(df_melted).mark_rect().encode(
#             x=alt.X('date', axis=alt.Axis(title="Date", format="%Y-%m-%d", labelAngle=-45)),
#             y=alt.Y('Habit', title="Habit"),
#             color=alt.Color('Completed_Num', 
#                             scale=alt.Scale(range=["#F87468", '#A9DFBF']), # Red-ish for 0, Green-ish for 1
#                             legend=alt.Legend(title="Completed", values=[0, 1], labelExpr="datum.value == 0 ? 'No' : 'Yes'")),
#             tooltip=[
#                 alt.Tooltip('date', title="Date", format="%Y-%m-%d"),
#                 'Habit',
#                 alt.Tooltip('Completed_Num', title="Done", format='d') # Format as integer
#             ]
#         ).properties(
#             title="Habit Completion Calendar"
#         ).interactive()

#         st.altair_chart(heatmap, use_container_width=True)

#     st.divider()

#     # --- Mood Distribution ---
#     st.header("Mood Distribution")
#     if "mood" in logs_df.columns:
#         mood_counts = logs_df["mood"].value_counts().reset_index()
#         mood_counts.columns = ["Mood", "Count"]

#         pie_chart = alt.Chart(mood_counts).mark_arc(outerRadius=120).encode(
#             theta=alt.Theta("Count", stack=True),
#             color=alt.Color("Mood", legend=alt.Legend(title="Mood")),
#             tooltip=["Mood", "Count"]
#         ).properties(
#             title="Your Moods at a Glance"
#         )
#         st.altair_chart(pie_chart, use_container_width=True)
#     else:
#         st.info("No mood data logged yet.")

# else:
#     st.info("No data to display. Go to the 'Daily Log' page to start tracking!")




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

# --- Page Configuration ---
# Must be the first Streamlit command
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
st.sidebar.title("🧠 MindTrack")
st.sidebar.markdown("Your personal wellness and habit tracker.")

# Updated navigation links
st.sidebar.page_link("streamlit_app.py", label="Progress Dashboard", icon="📊")
st.sidebar.page_link("pages/1_Daily_Log.py", label="Daily Log", icon="✍️")
st.sidebar.page_link("pages/3_AI_Insights.py", label="AI Insights", icon="✨")
st.sidebar.page_link("pages/0_Welcome.py", label="Welcome", icon="🏠") # New welcome page


# --- Helper Functions ---
# @st.cache_data(ttl=300) # Cache for 5 minutes
def load_data():
    """Fetches summary data from backend or falls back to local CSVs."""
    try:
        response = requests.get(SUMMARY_ENDPOINT)
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
    logs_df = pd.concat([df_sample, df_local]).drop_duplicates(subset=['date'], keep='last')
    
    if not logs_df.empty:
        logs_df['date'] = pd.to_datetime(logs_df['date'])
        # Simple summary calculation for fallback
        summary = {
            "total_logs": len(logs_df),
            "current_streak": 0, # Simple fallback
            "longest_streak": 0, # Simple fallback
        }
        st.toast("Displaying local/sample data.")
        return summary, logs_df
    
    return {}, pd.DataFrame(columns=['date'])

# --- Page UI ---
st.title("📊 Progress Dashboard")
st.markdown("Visualize your consistency and track your progress.")

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

    print(f"HABITS : {logs_df.columns} | {available_habits}")
    
    if not available_habits:
        st.warning("Habit columns (water, reading, meditation, exercise) not found in data.")
    else:
        # --- THIS IS THE NEW LOGIC ---
        # 1. Calculate total habits completed per day
        # Ensure habit columns are numeric before summing
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
                    edgecolor='white',
                    fillcolor='whitesmoke',
                    textcolor='gray',
                    linewidth=0.5,
                    yearlabels=True,
                    yearascending=True,
                    figsize=(12, 3), # We can suggest a size here
                    textformat='{:.0f}', 
                    textfiller='',
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