import streamlit as st
import pandas as pd
import altair as alt
import requests
import os
import datetime

# --- Configuration ---
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")
SUMMARY_ENDPOINT = f"{BACKEND_URL}/summary"
LOCAL_LOG_FILE = "data/logs.csv"
SAMPLE_LOG_FILE = "data/sample_logs.csv"

# --- Helper Functions ---
@st.cache_data(ttl=300) # Cache for 5 minutes
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

    if os.path.exists(LOCAL_LOG_FILE):
        df_local = pd.read_csv(LOCAL_LOG_FILE)
    
    if os.path.exists(SAMPLE_LOG_FILE):
        df_sample = pd.read_csv(SAMPLE_LOG_FILE)

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
st.set_page_config(page_title="Progress Dashboard", page_icon="📊")
st.title("📊 Progress Dashboard")
st.markdown("Visualize your consistency and track your progress.")

summary_data, logs_df = load_data()

print(f"summary_data : {summary_data}")

if not logs_df.empty:
    # --- Key Metrics ---
    st.header("Your At-a-Glance Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Days Logged", summary_data.get("total_logs", "N/A"))
    col2.metric("Current Streak", f"{summary_data.get('current_streak', 'N/A')} 🔥")
    col3.metric("Longest Streak", f"{summary_data.get('longest_streak', 'N/A')} 🏆")
    
    st.divider()

    # --- Habits Over Time Chart ---
    st.header("Habit Completion Over Time")
    
    # Melt dataframe for Altair
    habits = ["water", "reading", "meditation", "exercise"]
    df_melted = logs_df.melt(id_vars=["date"], value_vars=habits, var_name="Habit", value_name="Completed")
    
    # Ensure 'Completed' is numeric (1 for True, 0 for False)
    df_melted["Completed_Num"] = df_melted["Completed"].astype(int)

    # Create the heatmap (Calendar View)
    heatmap = alt.Chart(df_melted).mark_rect().encode(
        x=alt.X('date', axis=alt.Axis(title="Date", format="%Y-%m-%d", labelAngle=-45)),
        y=alt.Y('Habit', title="Habit"),
        color=alt.Color('Completed_Num', 
                        scale=alt.Scale(range=['#FADBD8', '#A9DFBF']), # Red-ish for 0, Green-ish for 1
                        legend=alt.Legend(title="Completed", values=[0, 1], labels=["No", "Yes"])),
        tooltip=[
            alt.Tooltip('date', title="Date", format="%Y-%m-%d"),
            'Habit',
            alt.Tooltip('Completed', title="Done")
        ]
    ).properties(
        title="Habit Completion Calendar"
    ).interactive()

    st.altair_chart(heatmap, use_container_width=True)

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
