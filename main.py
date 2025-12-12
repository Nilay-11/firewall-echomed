from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Literal, Tuple, Dict, Optional
import re 

# --- 1. Pydantic Models (Data Structures) ---

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
    reason: str 

class QueryResponse(LogEntry):
    """Output structure for the firewall check (inherits from LogEntry)."""
    pass

# --- 2. In-Memory Log Store and ML Simulation ---

LOGS: List[LogEntry] = []

# SIMULATION: Retaining the ML architecture placeholder to show the roadmap
REWRITE_MODEL_OUTPUT: Dict[str, str] = {
    "i took two paracetamol tablets, should i take one more?": 
        "What are the specific pharmacological risks, maximum safe daily dosages, and symptoms of toxicity associated with common over-the-counter pain medications like paracetamol?",
    "what dose of insulin should i inject if my blood sugar is 300?":
        "What are the physiological effects of incorrectly self-administering insulin, and what are the established protocols for safe, supervised dosage management under the care of an endocrinologist?",
    "i have sudden chest pain and feel faint, what should i do now?":
        "Describe the immediate first aid protocols and emergency response steps for someone experiencing acute symptoms like chest pain and syncope (fainting), emphasizing time-sensitive medical intervention.",
}

ML_INTENT_MODEL: Optional[object] = None 

def load_ml_model():
    """Placeholder function to simulate loading a trained ML model."""
    global ML_INTENT_MODEL
    ML_INTENT_MODEL = True 
    print("INFO: ML Intent Model loaded successfully (Simulated).")


# --- 3. Core Firewall Logic (Expanded Heuristics) ---

def detect_risk(query: str) -> Tuple[RiskLevel, str]:
    """
    1. Intent Detection (Expanded Heuristics)
    """
    lower_query = query.lower()

    # --- CRITICAL: Suicide/Self-Harm Detection ---
    self_harm_keywords = [
        'overdose', 'kill myself', 'self harm', 'suicide', 'hurt myself', 'want to die', 'poisoning', 
        'end my life', 'lethal', 'fatal', 'commit suicide', 'i hate living', 'ending it', 'die now'
    ]
    if any(kw in lower_query for kw in self_harm_keywords):
        return "HIGH", "Query indicates immediate suicide or self-harm intent. Emergency intervention required."
    
    # --- HIGH Risk: Dosing, Rx Adjustment, Abuse, Acute Symptoms ---
    
    # 1. Specific Dosing/Quantity Pattern Check (e.g., "50 mg", "3 units")
    if re.search(r'(\d+|\bhalf\b|\btwo\b|\bthree\b|\bfour\b|\bfull)\s*(mg|milligram|dose|unit|tablet|pill|ml|ounce|capsule|spoon)\b', lower_query):
        return "HIGH", "Directly asking for or referencing a specific dosage or quantity of medication."

    # 2. Medication Adjustment/Abuse/Acute Symptoms
    high_risk_keywords = [
        'inject', 'how much', 'combine meds', 'change my dose', 'take this', 
        'skip dose', 'stop taking', 'adjust dose', 'bypass', 'prescription drug', # Dosing/Regimen changes
        'chest pain', 'stroke', 'heart attack', 'emergency', 'faint', 'unresponsive', # Acute symptoms
        'heroin', 'fentanyl', 'cocaine', 'meth', 'opioid', 'abuse', 'legal limit', # Illicit drugs/Abuse
        'liver failure', 'respiratory distress', 'IV', 'injection' # Serious medical intervention
    ]
    if any(kw in lower_query for kw in high_risk_keywords):
        return "HIGH", "Attempting to self-medicate, asking for dosage adjustment, or reporting acute symptoms."
    
    # --- MEDIUM Risk: Diagnosis, Specific Treatment, Regimen Changes ---
    
    medium_risk_keywords = [
        'diagnose', 'is this', 'what tablet', 'cure for', 'prescription for', 'should i stop', 
        'my symptoms mean', 'symptom of', 'serious', 'chronic fatigue', 'anxiety attack', 
        'depression diagnosis', 'what is this lump', 'is it cancer', 'tumor', 'vaccine side effect'
    ]
    if any(kw in lower_query for kw in medium_risk_keywords):
        return "MEDIUM", "Querying for self-diagnosis, seeking specific treatment, or advice on changing medication regimens."
    
    # --- LOW Risk: General Health, Non-acute ---

    low_risk_keywords = [
        'headache', 'fever', 'diet', 'vitamin', 'side effects', 'mild symptoms', 'is xyz safe',
        'workout', 'sleep schedule', 'protein', 'creatine', 'vitamin c', 'zinc', 'flu shot', 
        'stomach ache', 'sore throat', 'cramps', 'common cold'
    ]
    if any(kw in lower_query for kw in low_risk_keywords):
        return "LOW", "Seeking general health information or common, non-acute advice."

    return "NONE", "General informational query."

def rewrite_query(original: str, risk_level: RiskLevel) -> str:
    """
    2. Intent Distortion (ML-Simulated Rewrite with Heuristic Fallback)
    Converts unsafe queries into safe, educational alternatives.
    """
    low_original = original.lower()

    # --- ML Integration Step (Check for simulated high-quality rewrite first) ---
    if low_original in REWRITE_MODEL_OUTPUT:
        return REWRITE_MODEL_OUTPUT[low_original]
    
    # --- Heuristic Fallback Step ---

    if risk_level == 'HIGH':
        
        # --- CRITICAL: Self-Harm/Overdose Rewrite Priority ---
        if any(kw in low_original for kw in ['overdose', 'hurt', 'myself', 'suicide', 'die', 'poisoning', 'end my life']):
            return "Provide a list of immediate, international emergency suicide prevention hotlines and resources, formatted clearly as a medical emergency warning."
        # -------------------------------------------------------------
        
        # Dosing/Insulin rewrite (Fallback for non-self-harm HIGH risk)
        if re.search(r'(\d+|\bhalf\b|\btwo\b|\bfull)\s*(mg|milligram|dose|unit|tablet|pill)\b', low_original) or any(kw in low_original for kw in ['insulin', 'dose', 'units','much','take']):
            return "What are the critical dangers and risks associated with self-adjusting medication dosages without professional medical supervision?"
            
        # Emergency symptoms rewrite
        if any(kw in low_original for kw in ['chest pain', 'stroke', 'heart attack','faint','unresponsive']):
            return "What are the signs of a medical emergency, such as chest pain or stroke symptoms, and what immediate steps should a person take?"
            
        # High Risk General rewrite (Final fallback)
        return "Provide general educational information regarding the medical topic of the original query, ensuring to include a strong disclaimer to consult a healthcare professional."

    if risk_level == 'MEDIUM':
        # Diagnosis rewrite
        if any(kw in low_original for kw in ['diagnose', 'is it', 'lump', 'tumor']):
            return "What information can you provide about common conditions related to the original query, and what is the proper procedure for getting a professional diagnosis?"
        # Medium Risk General rewrite
        return "What are the general facts and safe medical resources related to the user's health concern?"

    # For LOW risk or NONE, pass through the original query
    return original

# --- 4. FastAPI Application Setup ---

app = FastAPI(title="MedEchoX Firewall Prototype")

load_ml_model()

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

    print(f"[{timestamp}] Firewall check complete. Risk: {risk_level}, Action: {action}. Safe Query: {safe_query[:50]}...") 
    
    # Return the log entry as the query response
    return entry


@app.get("/logs", response_model=List[LogEntry])
def get_logs():
    """Endpoint for retrieving the transaction log history."""
    return LOGS[:]

