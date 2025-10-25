# 🧠 MindTrack - Frontend

This is the Streamlit frontend for the MindTrack wellness and habit tracker.

**MindTrack Ai** is a backend service for a personal mental health tracker that helps users log daily habits, track moods, and get AI-based mood predictions from journal texts.

---

## Project Structure

frontend/  
├── streamlit_app.py              – Main welcome page  
├── pages/  
│   ├── 1_Daily_Log.py            – Page for user input  
│   ├── 2_Progress_Dashboard.py   – Page for charts  
│   └── 3_AI_Insights.py          – Page for sentiment analysis  
├── utils/  
│   └── helpers.py                – Helper functions  
├── data/  
│   ├── logs.csv                  – Local fallback logs  
│   └── sample_logs.csv           – Sample data for judges  
├── requirements.txt              – Python dependencies  
└── README.md                     – This file  

---

## Running Locally

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Streamlit app

```bash
streamlit run streamlit_app.py
```

Note: The app expects the backend service to be running local, by default at http://127.0.0.1:5000.

---

## Deployment

This app is designed to be deployed on Streamlit Community Cloud:

- Push this repository to GitHub
- Sign up for Streamlit Community Cloud
- Connect your GitHub repo and deploy.

IMPORTANT: You must set a Secret (Environment Variable) in Streamlit Cloud:

```bash
BACKEND_URL = "https://shivenduu-mindtrack-backend.hf.space"

APP_URL = "streamlit app urk"

GEMINI_API_KEY = 'your gemini access token'
```

## Contact

For any questions regarding this backend:
- **Developer**: Shivendu Kumar, Atharv Mishra
- **Email**: shiv.end.you@gmail.com, mishra17atharv@gmail.com

---