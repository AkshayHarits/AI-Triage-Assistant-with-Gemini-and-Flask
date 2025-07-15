# main.py
import os
from dotenv import load_dotenv

load_dotenv()

from triage_assistant import create_graph

graph = create_graph()

print("\n Hospital - AI Triage Assistant")
print("--------------------------------------------------")

final_state = graph.invoke({})
