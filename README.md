🧠 MindTrack - Frontend

This is the Streamlit frontend for the MindTrack wellness and habit tracker.

Project Structure

frontend/
├── streamlit_app.py         # Main welcome page
├── pages/
│   ├── 1_Daily_Log.py       # Page for user input
│   ├── 2_Progress_Dashboard.py # Page for charts
│   └── 3_AI_Insights.py     # Page for sentiment analysis
├── utils/
│   └── helpers.py           # Helper functions
├── data/
│   ├── logs.csv             # Local fallback logs
│   └── sample_logs.csv      # Sample data for judges
├── requirements.txt         # Python dependencies
└── README.md                # This file


Running Locally

Install dependencies:

pip install -r requirements.txt


Run the Streamlit app:

streamlit run streamlit_app.py


Note: The app expects the backend service to be running, by default at http://127.0.0.1:5000.

Deployment

This app is designed to be deployed on Streamlit Community Cloud.

Push this repository to GitHub.

Sign up for Streamlit Community Cloud.

Connect your GitHub repo and deploy.

IMPORTANT: You must set a Secret (Environment Variable) in Streamlit Cloud:

BACKEND_URL = https://your-flask-app-url.onrender.com