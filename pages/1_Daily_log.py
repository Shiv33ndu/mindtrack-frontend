import streamlit as st
import pandas as pd
import requests
import datetime
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
BACKEND_URL = os.getenv("BACKEND_URL")
LOG_ENDPOINT = f"{BACKEND_URL}/log"
LOCAL_LOG_FILE = "data/logs.csv"

print(f"BACKEND_URL : {BACKEND_URL}")

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
    page_title="MindTrack - Daily Log",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Helper to load images ---
# @st.cache_data
def load_image(path):
    """Safely loads an image, returns None if not found."""
    try:
        # Assumes your assets folder is at the root, relative to where streamlit_app.py is
        return Image.open(path)
    except FileNotFoundError:
        st.warning(f"Icon not found at {path}")
        return None

# --- Load Icons ---
water_icon = load_image("assets/icons/water.png")
read_icon = load_image("assets/icons/reading.png")
meditate_icon = load_image("assets/icons/meditation.png")
exercise_icon = load_image("assets/icons/exercise.png")


# --- Helper Functions ---
def save_log_locally(log_entry):
    """Saves the log entry to a local CSV file as a fallback."""
    try:
        df_entry = pd.DataFrame([log_entry])
        if not os.path.exists(LOCAL_LOG_FILE):
            df_entry.to_csv(LOCAL_LOG_FILE, index=False)
        else:
            df_entry.to_csv(LOCAL_LOG_FILE, mode='a', header=False, index=False)
        return True
    except Exception as e:
        st.error(f"Failed to save log locally: {e}")
        return False

def save_log_to_backend(log_entry):
    """Tries to save the log entry to the backend."""
    try:
        response = requests.post(LOG_ENDPOINT, json=log_entry)
        if response.status_code == 201:
            return True
        else:
            st.warning(f"Backend save failed (Status {response.status_code}): {response.text}. Saving locally.")
            return False
    except requests.exceptions.ConnectionError as e:
        st.warning(f"Could not connect to backend: {e}. Saving locally.")
        return False

# --- Page UI ---
st.set_page_config(page_title="Daily Log", page_icon="✍️")
st.title("✍️ Daily Log")
st.markdown("Log your habits, mood, and thoughts for today.")

# Use today's date
today = datetime.date.today()
today_str = today.strftime("%Y-%m-%d")

st.info(f"Logging for: **{today_str}**")


# --- Form ---
with st.form("daily_log_form"):
    st.subheader("Habit Check-in")
    col1, col2 = st.columns(2)
    with col1:
        # --- Water ---
        sub_col1, sub_col2 = st.columns([1, 5]) # [icon_width, checkbox_width]
        with sub_col1:
            if water_icon:
                st.image(water_icon, width=128)
            else:
                st.write("💧") # Fallback if image not found
        with sub_col2:
            water = st.checkbox("Water Intake (8 glasses)")
        
        # --- Reading ---
        sub_col3, sub_col4 = st.columns([1, 5])
        with sub_col3:
            if read_icon:
                st.image(read_icon, width=128)
            else:
                st.write("📖") # Fallback
        with sub_col4:
            # Note: Using 'reading' to match your CSV header from last time
            reading = st.checkbox("Read (15 mins)")

    with col2:
        # --- Meditate ---
        sub_col5, sub_col6 = st.columns([1, 5])
        with sub_col5:
            if meditate_icon:
                st.image(meditate_icon, width=128)
            else:
                st.write("🧘") # Fallback
        with sub_col6:
            meditation = st.checkbox("Meditate (5 mins)")

        # --- Exercise ---
        sub_col7, sub_col8 = st.columns([1, 5])
        with sub_col7:
            if exercise_icon:
                st.image(exercise_icon, width=128)
            else:
                st.write("🏃") # Fallback
        with sub_col8:
            exercise = st.checkbox("Exercise (20 mins)")

    st.divider()

    st.subheader("Write your Journal, AI will auto predict your mood")
    # mood = st.selectbox(
    #     "How are you feeling today?",
    #     ("😄 Happy", "😐 Neutral", "😔 Sad", "😠 Angry"),
    #     index=0
    # )
    
    journal = st.text_area(
        "Write a short journal entry (optional):",
        height=150,
        placeholder="What's on your mind? Your entry will be used for AI sentiment analysis."
    )

    submitted = st.form_submit_button("Save Today's Log", type="primary", use_container_width=True)

# --- Form Submission Logic ---
if submitted:
    # 1. Validation
    if not journal.strip():
        st.warning("Please write a journal entry. The AI needs it to analyze your mood.")
    else:
        try:
            with st.spinner("AI is analyzing your mood..."):
                # 2. Call Backend for Mood Prediction
                predict_payload = {"text": journal}
                predict_response = requests.post(f"{BACKEND_URL}/predict_mood", json=predict_payload, timeout=20)
                predict_response.raise_for_status() # Error if API fails
                
                prediction_data = predict_response.json()
                predicted_mood = prediction_data.get("mood", "Neutral") # predict mood
                
            placeholder = st.empty()
            placeholder.success(f"AI analyzed your mood as: **{predicted_mood}**. Saving log...")

            # 3. Prepare Full Log Data
            log_date_str = datetime.date.today().isoformat()
            new_log_data = {
                "date": log_date_str,
                "exercise": 1 if exercise else 0,
                "water": 1 if water else 0,
                "reading": 1 if reading else 0,
                "meditation": 1 if meditation else 0,
                "mood": predicted_mood,
                "journal_text": journal
            }

            # 4. Send to Backend /log endpoint
            with st.spinner("Saving to backend..."):
                log_response = requests.post(f"{BACKEND_URL}/log", json=new_log_data, timeout=10)
                log_response.raise_for_status()
                # Use success toast for a non-blocking final message
                placeholder.success(f"Successfully saved log for {log_date_str}!", icon="🎉")

        except requests.RequestException as e:
            st.error(f"**Save Failed!**\n\nCould not connect to the backend: {e}\n\n**Please try submitting again.**")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}. Please try again.")

    
