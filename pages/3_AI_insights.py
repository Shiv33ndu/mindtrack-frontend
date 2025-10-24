import streamlit as st
import requests
import os

# --- Configuration ---
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")
PREDICT_ENDPOINT = f"{BACKEND_URL}/predict_mood"

# --- Helper Functions ---
@st.cache_data(ttl=3600) # Cache for 1 hour
def get_affirmation():
    """Fetches a random affirmation. Uses a fallback."""
    try:
        # Using a simple, free affirmation API
        response = requests.get("https://www.affirmations.dev/")
        if response.status_code == 200:
            return response.json().get("affirmation", "You are doing great!")
    except requests.exceptions.RequestException:
        pass # Fallback to default
    return "You are capable of amazing things. Keep going!"

def get_mood_prediction(journal_text):
    """Sends journal text to backend for sentiment analysis."""
    try:
        response = requests.post(PREDICT_ENDPOINT, json={"text": journal_text})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error from AI model (Status {response.status_code}): {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the AI backend. Please try again later.")
        return None

# --- Page UI ---
st.set_page_config(page_title="AI Insights", page_icon="✨")
st.title("✨ AI Insights")
st.markdown("Get a deeper understanding of your thoughts and a dose of motivation.")

# --- Motivational Quote ---
st.subheader("💡 Your Daily Affirmation")
affirmation = get_affirmation()
st.info(f"**{affirmation}**")

st.divider()

# --- Sentiment Analysis ---
st.subheader("🤖 Analyze Your Journal")
st.markdown("Curious about the sentiment of your thoughts? Paste in a journal entry below.")

journal_text = st.text_area(
    "Enter journal text here:",
    height=200,
    placeholder="Type or paste your journal entry... The AI will analyze its sentiment."
)

if st.button("Analyze Sentiment", type="primary", use_container_width=True):
    if journal_text.strip():
        with st.spinner("AI is analyzing your text..."):
            prediction = get_mood_prediction(journal_text)
            
            if prediction:
                sentiment = prediction.get("sentiment", "UNKNOWN")
                score = prediction.get("score", 0)
                message = prediction.get("message", "Analysis complete.")
                
                st.subheader("Analysis Result")
                
                # Display sentiment with an icon
                if sentiment == "POSITIVE":
                    st.success(f"**Sentiment: {sentiment}** (Score: {score:.2f})")
                elif sentiment == "NEGATIVE":
                    st.error(f"**Sentiment: {sentiment}** (Score: {score:.2f})")
                else:
                    st.info(f"**Sentiment: {sentiment}** (Score: {score:.2f})")
                
                st.markdown(f"**A note from your AI assistant:**")
                st.write(message)
    else:
        st.warning("Please enter some text to analyze.")
