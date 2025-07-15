# AI Triage Assistant with Gemini and Flask

An intelligent healthcare triage assistant that classifies patient symptoms into medical categories (General, Emergency, Mental Health) using Google's Gemini 1.5. It provides instant feedback and sends a detailed diagnosis report via email.

---

## Features

- Simple web interface using Flask  
- Symptom classification using Gemini 1.5 Flash  
- Automated email report with recommendations  
- Secure `.env`-based configuration  
- Structured state flow with LangGraph  

---

## Project Structure

```
AI-Triage-Assistant/
│
├── app.py                 # Flask web app entry point
├── triage_assistant.py    # Core logic, LangGraph workflow, Gemini integration
├── requirements.txt       # Python dependencies
├── .env                   # Your private credentials (not uploaded)
├── templates/
│   ├── index.html         # Input form for user data
│   └── result.html        # Output diagnosis report
└── venv/                  # Python virtual environment (ignored in Git)
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AI-Triage-Assistant.git
cd AI-Triage-Assistant
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```ini
GOOGLE_API_KEY=your_gemini_api_key
SENDER_EMAIL=your_gmail_address
EMAIL_APP_PASSWORD=your_app_specific_password
```

Note: Never share or push your `.env` file to GitHub.

---

## Run the App

```bash
python app.py
```

Visit: http://127.0.0.1:5000

---

## Output Example (Email Report)

- Patient Name, Age, and Symptoms  
- Classification for each symptom  
- Recommendation summary  
- Timestamped diagnosis  
- Delivered as an HTML email

---

## To-Do / Future Work

- Add user authentication  
- Connect to real hospital triage systems  
- Log past reports  
- Multilingual support  
- Enhance UI styling  
- Deploy online (Render, Railway, etc.)

---

## Author

Akshay S Harits  
IIT Hyderabad

---

## Acknowledgements

- LangGraph  
- LangChain Google GenAI  
- Flask  
- Google Gemini 1.5
