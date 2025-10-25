# import streamlit as st
# import requests
# import os

# # --- Configuration ---
# BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")
# PREDICT_ENDPOINT = f"{BACKEND_URL}/predict_mood"

# # --- Helper Functions ---
# @st.cache_data(ttl=3600) # Cache for 1 hour
# def get_affirmation():
#     """Fetches a random affirmation. Uses a fallback."""
#     try:
#         # Using a simple, free affirmation API
#         response = requests.get("https://www.affirmations.dev/")
#         if response.status_code == 200:
#             return response.json().get("affirmation", "You are doing great!")
#     except requests.exceptions.RequestException:
#         pass # Fallback to default
#     return "You are capable of amazing things. Keep going!"

# def get_mood_prediction(journal_text):
#     """Sends journal text to backend for sentiment analysis."""
#     try:
#         response = requests.post(PREDICT_ENDPOINT, json={"text": journal_text})
#         if response.status_code == 200:
#             return response.json()
#         else:
#             st.error(f"Error from AI model (Status {response.status_code}): {response.text}")
#             return None
#     except requests.exceptions.ConnectionError:
#         st.error("Could not connect to the AI backend. Please try again later.")
#         return None

# # --- Page UI ---
# st.set_page_config(page_title="AI Insights", page_icon="✨")
# st.title("✨ AI Insights")
# st.markdown("Get a deeper understanding of your thoughts and a dose of motivation.")

# # --- Motivational Quote ---
# st.subheader("💡 Your Daily Affirmation")
# affirmation = get_affirmation()
# st.info(f"**{affirmation}**")

# st.divider()

# # --- Sentiment Analysis ---
# st.subheader("🤖 Analyze Your Journal")
# st.markdown("Curious about the sentiment of your thoughts? Paste in a journal entry below.")

# journal_text = st.text_area(
#     "Enter journal text here:",
#     height=200,
#     placeholder="Type or paste your journal entry... The AI will analyze its sentiment."
# )

# if st.button("Analyze Sentiment", type="primary", use_container_width=True):
#     if journal_text.strip():
#         with st.spinner("AI is analyzing your text..."):
#             prediction = get_mood_prediction(journal_text)
            
#             if prediction:
#                 sentiment = prediction.get("sentiment", "UNKNOWN")
#                 score = prediction.get("score", 0)
#                 message = prediction.get("message", "Analysis complete.")
                
#                 st.subheader("Analysis Result")
                
#                 # Display sentiment with an icon
#                 if sentiment == "POSITIVE":
#                     st.success(f"**Sentiment: {sentiment}** (Score: {score:.2f})")
#                 elif sentiment == "NEGATIVE":
#                     st.error(f"**Sentiment: {sentiment}** (Score: {score:.2f})")
#                 else:
#                     st.info(f"**Sentiment: {sentiment}** (Score: {score:.2f})")
                
#                 st.markdown(f"**A note from your AI assistant:**")
#                 st.write(message)
#     else:
#         st.warning("Please enter some text to analyze.")


import streamlit as st
import requests
import os
from datetime import datetime

# ----- To hide default page show -----
st.markdown("""
    <style>
        [data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Page Config ---
st.set_page_config(
    page_title="AI Insights",
    page_icon="🤖",
    layout="wide"
)

# --- Backend URL (for consistency, though not used here) ---
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")
GEMINI_API_KEY = 'sdfhsdjfhjsdhfkdshfkdsjhfkdshfkjdsf'#st.secrets.get("GEMINI_API_KEY")

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
    st.page_link("pages/1_Daily_Log.py", label="Daily Log", icon="✏️")
    st.page_link("pages/3_AI_Insights.py", label="AI Insights", icon="🤖")
    st.page_link("pages/0_Welcome.py", label="About", icon="👋")

# --- Helper Functions ---

# @st.cache_data(ttl=600) # Cache the insight for 10 minutes
def get_gemini_insight(thought_text, api_key):
    """
    Calls the Gemini API to get an insight on a user's thought.
    """
    system_prompt = (
        "You are an AI wellness coach and mindset analyst. "
        "A user is sharing a raw, current thought. Your job is to analyze it "
        "and provide a brief, constructive, and supportive insight in 2-4 sentences. "
        "Do not be generic. Focus on their potential mindset, underlying feelings, or "
        "cognitive patterns you observe. Start your response directly with the insight."
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": thought_text}]
        }],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status() # Raise error for bad responses
        
        result = response.json()
        
        # --- Safely parse the response ---
        if not result.get('candidates'):
            return "Error: The AI model returned an empty response. This might be due to safety flags."
            
        candidate = result['candidates'][0]
        
        if 'content' not in candidate or 'parts' not in candidate['content']:
             return "Error: Could not parse AI response (missing content)."
             
        text = candidate['content']['parts'][0].get('text', "Error: Could not parse AI response text.")
        return text
        
    except requests.exceptions.RequestException as e:
        st.error(f"API Request Failed: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Main Page ---
st.title("🤖 AI Instant Insights")
st.markdown(
    "Wanna have some insights on the thought or feeling you're having *right now*."
)

st.divider()

# --- Check for API Key ---
if not GEMINI_API_KEY:
    st.error(
        "**AI Insight Service Not Configured!**\n\n"
        "To use this feature, the app owner needs to:\n"
        "1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).\n"
        "2. Add it to this app's Streamlit secrets as `GEMINI_API_KEY`."
    )
else:
    thought = st.text_area(
        "What's on your mind right now?",
        height=150,
        placeholder="e.g., 'I feel overwhelmed by my projects and don't know where to start.' or 'I'm feeling really happy about a conversation I just had.'",
        label_visibility="collapsed"
    )

    if st.button("Analyze My Thought", type="primary", use_container_width=True):
        if thought:
            with st.spinner("AI is analyzing your thought..."):
                insight = get_gemini_insight(thought, GEMINI_API_KEY)
                
                if insight:
                    st.subheader("Your Thought:")
                    st.markdown(f"> {thought}")
                    st.subheader("AI Insight:")
                    st.success(insight)
        else:
            st.warning("Please enter a thought to analyze.")

