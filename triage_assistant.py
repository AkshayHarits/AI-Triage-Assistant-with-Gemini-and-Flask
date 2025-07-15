# triage_assistant.py

import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from typing import TypedDict, List

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# -----------------------------------------------
# STEP 1: Load environment variables
# -----------------------------------------------
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

if not all([GOOGLE_API_KEY, EMAIL_APP_PASSWORD, SENDER_EMAIL]):
    raise EnvironmentError("Missing API keys or email credentials in .env file.")

os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY

# -----------------------------------------------
# STEP 2: Initialize Gemini
# -----------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash-latest",
    temperature=0.2
)

# -----------------------------------------------
# STEP 3: Define structured state
# -----------------------------------------------
class TriageState(TypedDict, total=False):
    name: str
    age: str
    email: str
    symptoms: List[str]
    current_symptom: str
    current_category: str
    recommendation: str
    done: bool

# -----------------------------------------------
# STEP 4: Define node functions
# -----------------------------------------------
def get_user_details(state: TriageState) -> TriageState:
    return {
        'name': input("Please enter your name: "),
        'age': input("Please enter your age: "),
        'email': input("Please enter your email ID: "),
        'symptoms': [],
        'done': False,
    }

def get_symptom(state: TriageState) -> TriageState:
    symptom = input(f"{state['name']}, please enter your symptom (or type 'done' to finish): ")
    if symptom.lower() == 'done':
        return {'done': True}
    updated_symptoms = state['symptoms'] + [symptom]
    return {'current_symptom': symptom, 'symptoms': updated_symptoms, 'done': False}

#def classify_symptom(state: TriageState) -> TriageState:
    prompt = (
        "You are a helpful Medical Assistant. Classify the following symptom into one category:"
        "\n- General\n- Emergency\n- Mental Health\n"
        f"Symptom: {state['current_symptom']}\n"
        "Respond with ONLY one word (General, Emergency, Mental Health)."
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    category = response.content.strip()
    print(f"LLM classifies the symptom as: {category}")
    return {'current_category': category}

def classify_patient(state: TriageState) -> TriageState:
    symptoms = state.get("symptoms", [])
    symptom_list = "\n".join(f"- {s}" for s in symptoms)

    prompt = (
        "You are an AI triage assistant. Based on the list of patient symptoms, "
        "classify the patient into one of the following categories:\n"
        "- General\n- Emergency\n- Mental Health\n\n"
        f"Symptoms:\n{symptom_list}\n\n"
        "Respond with only one word: General, Emergency, or Mental Health."
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    category = response.content.strip().lower()

    if "emergency" in category:
        reco = f"The patient's symptoms indicate an emergency. Please proceed to the emergency ward."
    elif "mental" in category:
        reco = f"The patient's symptoms suggest a mental health concern. Connect them to a counselor."
    else:
        reco = f"The symptoms are general. Proceed to the general outpatient department."

    state["recommendation"] = reco
    return state



def symptom_router(state: TriageState) -> str:
    if state.get('done'):
        return "send_email"
    cat = state['current_category'].lower()
    if "general" in cat:
        return "general"
    elif "emergency" in cat:
        return "emergency"
    elif "mental" in cat:
        return "mental_health"
    return "general"

def general_node(state: TriageState) -> TriageState:
    msg = f"'{state['current_symptom']}' seems to be a general symptom. {state['name']}, please proceed to the general ward."
    print(msg)
    return {"recommendation": msg}

def emergency_node(state: TriageState) -> TriageState:
    msg = f"'{state['current_symptom']}' appears to be an emergency. {state['name']}, you are being sent to the emergency ward immediately."
    print(msg)
    return {"recommendation": msg}

def mental_health_node(state: TriageState) -> TriageState:
    msg = f"'{state['current_symptom']}' indicates a mental health issue. {state['name']}, connecting you with our counselor."
    print(msg)
    return {"recommendation": msg}

def send_email(state: TriageState) -> TriageState:
    html_summary = f"""
    <html>
      <body>
        <h2>Symptom Diagnosis Report</h2>
        <p><strong>Patient Name:</strong> {state['name']}</p>
        <p><strong>Age:</strong> {state['age']}</p>
        <p><strong>Symptoms Reported:</strong> {', '.join(state['symptoms'])}</p>
        <p><strong>Diagnosis Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Recommendation:</strong> {state.get('recommendation', 'N/A')}</p>
      </body>
    </html>
    """
    print("\nSending HTML Email Report to", state['email'])

    msg = EmailMessage()
    msg.set_content("Please view this email in HTML.")
    msg.add_alternative(html_summary, subtype='html')
    msg['Subject'] = 'Your Symptom Diagnosis Report'
    msg['From'] = SENDER_EMAIL
    msg['To'] = state['email']

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, EMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
    return {}

# -----------------------------------------------
# STEP 5: Create and return the graph
# -----------------------------------------------
#def create_graph():
    builder = StateGraph(TriageState)

    builder.set_entry_point("get_user_details")

    builder.add_node("get_user_details", get_user_details)
    builder.add_node("get_symptom", get_symptom)
    builder.add_node("classify", classify_symptom)
    builder.add_node("general", general_node)
    builder.add_node("emergency", emergency_node)
    builder.add_node("mental_health", mental_health_node)
    builder.add_node("send_email", send_email)

    builder.add_edge("get_user_details", "get_symptom")
    builder.add_edge("get_symptom", "classify")

    builder.add_conditional_edges("classify", symptom_router, {
        "general": "general",
        "emergency": "emergency",
        "mental_health": "mental_health",
        "send_email": "send_email"
    })

    builder.add_edge("general", "get_symptom")
    builder.add_edge("emergency", "get_symptom")
    builder.add_edge("mental_health", "get_symptom")
    builder.add_edge("send_email", END)

    return builder.compile()


def create_web_graph():
    builder = StateGraph(TriageState)
    builder.set_entry_point("classify_patient")

    builder.add_node("classify_patient", classify_patient)
    builder.add_node("send_email", send_email)

    builder.add_edge("classify_patient", "send_email")
    builder.add_edge("send_email", END)

    return builder.compile()

