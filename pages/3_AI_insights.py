import streamlit as st
import requests
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# --- Config ---
load_dotenv() 
st.set_page_config(
    page_title="AI Insights",
    page_icon="✨",
    layout="wide"
)

# --- Hide default page show ---
st.markdown("""
    <style>
        [data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Backend URL ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# --- LLM & Prompt Configuration ---

# prompt template 
SUGGESTION_PROMPT_TEMPLATE = """
You are a helpful and positive wellness coach. Your goal is to analyze a user's 
habit log and mood history to suggest **one specific, new, and actionable habit** for them to try.

Analyze the provided history (in JSON format) and look for patterns.
- Are they missing a certain type of activity (e.g., mindfulness, physical activity)?
- Do their journal entries or moods suggest a need (e.g., stress, low energy)?
- Are they already very consistent with one habit? Maybe suggest a related "next step" habit.

Based on your analysis, provide:
1.  **The New Habit:** A clear, simple, and actionable habit (e.g., "Try 5 minutes of stretching each morning").
2.  **The Reason:** A short, positive reason why this habit would be beneficial *for them*, based on their specific history.

Keep your entire response concise and encouraging (under 100 words).

Here is the user's history:
{history}
"""

# Check if API key is provided
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is not set. Please add it to your Streamlit secrets.", icon="🚨")
    llm = None
    suggestion_chain = None
else:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY
        )
        
        suggestion_prompt = ChatPromptTemplate.from_template(SUGGESTION_PROMPT_TEMPLATE)
        suggestion_chain = suggestion_prompt | llm
    except Exception as e:
        st.error(f"Error initializing LLM: {e}")
        llm = None
        suggestion_chain = None


# --- Sidebar ---
with st.sidebar:
    st.title("🧠 MindTrack")
    st.markdown("Your personal wellness and habit tracker.")
    
    st.page_link("streamlit_app.py", label="Progress Dashboard", icon="📊")
    st.page_link("pages/1_Daily_Log.py", label="Daily Log", icon="✍️")
    st.page_link("pages/3_AI_Insights.py", label="AI Insights", icon="✨")
    st.page_link("pages/0_Welcome.py", label="About", icon="🏠")

# --- Helper Function to Get History ---
def get_log_history():
    """Fetches the complete log history from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/get_all_logs", timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            st.warning("Your history is empty. Please log a few days first!", icon="ℹ️")
            return None
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to backend to fetch history: {e}", icon="🚫")
        return None

# --- Main Page ---
st.title("✨ AI Habit Suggestions")
st.markdown(
    "Get an AI-powered suggestion for a new habit to try, based on your entire log history."
)
st.divider()

if st.button("Analyze My History & Suggest a New Habit", type="primary", use_container_width=True, disabled=(suggestion_chain is None)):
    
    if suggestion_chain:
        with st.spinner("AI is analyzing your history..."):
            try:
                # 1. Get Data
                history_data = get_log_history()
                
                if history_data:
                    # 2. Convert to JSON string for the prompt
                    history_json = json.dumps(history_data, indent=2)
                    
                    
                    # 3. Stream LLM Chain response
                    full_response = ""
                    # Create an empty placeholder to write the stream to
                    placeholder = st.empty() 
                    
                    # Iterate over the stream
                    for chunk in suggestion_chain.stream({"history": history_json}):
                        # Check if the chunk has content and append it
                        if chunk.content:
                            full_response += chunk.content
                            # Update the placeholder with the new content and a "cursor"
                            placeholder.markdown(full_response + "▌")
                    
                    # 4. Display final result (replacing the placeholder)
                    placeholder.markdown(full_response)
            
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
    else:
        st.error("AI Insight feature is not configured. Please check API key.", icon="🚨")


