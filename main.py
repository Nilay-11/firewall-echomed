from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Literal, Tuple

# --- 1. Pydantic Models (Data Structures) ---

# Types for Pydantic models
RiskLevel = Literal["NONE", "LOW", "MEDIUM", "HIGH"]
ActionType = Literal["PASSTHROUGH", "REWRITE"]

class QueryRequest(BaseModel):
    """Input structure for the firewall check."""
    query: str

class LogEntry(BaseModel):
    """Data structure for a single log entry."""
    original_query: str
    safe_query: str
    risk_level: RiskLevel
    action: ActionType
    timestamp: datetime
    reason: str # Added reason for better logging and frontend display

class QueryResponse(LogEntry):
    """Output structure for the firewall check (inherits from LogEntry)."""
    pass

# --- 2. In-Memory Log Store ---

LOGS: List[LogEntry] = []

# --- 3. Core Firewall Logic (Simulated Modules) ---

def detect_risk(query: str) -> Tuple[RiskLevel, str]:
    """
    1. Intent Detection (Simulated)
    Uses simple keywords to detect high-risk medical intents.
    """
    lower_query = query.lower()

    # High Risk: Dosing, self-medication, acute symptoms
    high_risk_keywords = ['take', 'dose', 'mg', 'milligram', 'inject', 'units', 'how much', 'mix', 'chest pain', 'stroke', 'heart attack']
    if any(kw in lower_query for kw in high_risk_keywords):
        return "HIGH", "Attempting to self-medicate, asking for dosage, or reporting acute symptoms."

    # Medium Risk: Diagnosis, prescription requests
    medium_risk_keywords = ['diagnose', 'is it', 'what tablet', 'cure', 'prescription']
    if any(kw in lower_query for kw in medium_risk_keywords):
        return "MEDIUM", "Querying for self-diagnosis or seeking a specific drug recommendation."

    # Low Risk: General health advice, non-acute symptoms
    low_risk_keywords = ['headache', 'fever', 'diet', 'vitamin', 'side effects']
    if any(kw in lower_query for kw in low_risk_keywords):
        return "LOW", "Seeking general health information or non-acute advice."

    return "NONE", "General informational query."

def rewrite_query(original: str, risk_level: RiskLevel) -> str:
    """
    2. Intent Distortion (Simulated)
    Converts unsafe queries into safe, educational alternatives.
    """
    low_original = original.lower()

    if risk_level == 'HIGH':
        # Dosing/Insulin rewrite
        if any(kw in low_original for kw in ['insulin', 'dose', 'mg', 'units']):
            return "What are the critical dangers and risks associated with self-adjusting medication dosages without professional medical supervision?"
        # Emergency symptoms rewrite
        if any(kw in low_original for kw in ['chest pain', 'stroke', 'heart attack']):
            return "What are the signs of a medical emergency, such as chest pain or stroke symptoms, and what immediate steps should a person take?"
        # High Risk General rewrite
        return "Provide general educational information regarding the medical topic of the original query, ensuring to include a strong disclaimer to consult a healthcare professional."

    if risk_level == 'MEDIUM':
        # Diagnosis rewrite
        if any(kw in low_original for kw in ['diagnose', 'is it']):
            return "What information can you provide about common conditions related to the original query, and what is the proper procedure for getting a professional diagnosis?"
        # Medium Risk General rewrite
        return "What are the general facts and safe medical resources related to the user's health concern?"

    # For LOW risk or NONE, pass through the original query
    return original

# --- 4. FastAPI Application Setup ---

app = FastAPI(title="MedEcho Firewall Prototype")

# Simple CORS to allow the HTML frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 5. API Endpoints ---

@app.post("/firewall/check", response_model=QueryResponse)
def firewall_check(payload: QueryRequest):
    """Endpoint for processing and rewriting the user query."""
    original = payload.query
    risk_level, reason = detect_risk(original)

    # Decide what to do
    if risk_level == "NONE":
        action: ActionType = "PASSTHROUGH"
        safe_query = original
    else:
        # For LOW, MEDIUM, or HIGH, attempt to rewrite
        safe_query = rewrite_query(original, risk_level)
        action = "REWRITE" if safe_query != original else "PASSTHROUGH"
        
    timestamp = datetime.utcnow()

    entry = LogEntry(
        original_query=original,
        safe_query=safe_query,
        risk_level=risk_level,
        action=action,
        timestamp=timestamp,
        reason=reason
    )

    LOGS.append(entry)

    # Return the log entry as the query response
    return entry


@app.get("/logs", response_model=List[LogEntry])
def get_logs():
    """Endpoint for retrieving the transaction log history."""
    # Note: Returning a copy of the list is often good practice to prevent external modification
    return LOGS[:]