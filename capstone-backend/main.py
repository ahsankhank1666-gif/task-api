import os
import json
from datetime import datetime
from typing import List
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware  
from pydantic import BaseModel
from supabase import create_client, Client
from upstash_redis import Redis
import google.generativeai as genai
from reportlab.pdfgen import canvas

# ---------------------------------------------------------
# 1. Configuration & Client Setup
# ---------------------------------------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://zeihtmelncooplzcatya.supabase.co/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InplaWh0bWVsbmNvb3BsemNhdHlhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MDMxMDM2NSwiZXhwIjoyMTA1ODg2MzY1fQ.ZMcw5tCh9JJHIKrMULgz1lS3zkv2pRoMTjuzI7Elp-4")
UPSTASH_REDIS_URL = os.environ.get("UPSTASH_REDIS_REST_URL", "https://liked-arachnid-301598.upstash.io")
UPSTASH_REDIS_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "gQAAAAAABJoeAAIgcDFlNDYzNzIxYWU2Mjg0ZDU0YWJiNWRjMmIyYmEyMjBjZA")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6IPeaa4gM41XDZLyxoOifcbc6d1Wt7agpBZlwNOZFjbpA")

# Initialize Clients
app = FastAPI(title="CBT Journal AI API", description="Cognitive Distortion Detection Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows your Flutter web app to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
redis = Redis(url=UPSTASH_REDIS_URL, token=UPSTASH_REDIS_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
llm_model = genai.GenerativeModel('gemini-1.5-flash')

# ---------------------------------------------------------
# 2. Pydantic Models (Data Validation)
# ---------------------------------------------------------
class JournalInput(BaseModel):
    raw_text: str

class FullJournalResponse(BaseModel):
    entry_id: str
    user_id: str
    raw_text: str
    distortions: List[str]
    reframed_thought: str
    created_at: str

class PastEntryResponse(BaseModel):
    id: str
    user_id: str
    raw_text: str
    created_at: str

# ---------------------------------------------------------
# 3. Core Logic: LLM Pipeline & PDF Generation
# ---------------------------------------------------------
def analyze_thought_with_llm(raw_text: str) -> dict:
    prompt = f"""
    You are an expert Cognitive Behavioral Therapy (CBT) assistant.
    Analyze the following user journal entry: "{raw_text}"
    Identify any common cognitive distortions (e.g., Catastrophizing, All-or-Nothing Thinking, Mind Reading).
    Provide a constructive, empathetic reframed thought.
    Return ONLY a raw JSON object with NO markdown or extra text:
    {{
        "distortions": ["Distortion1", "Distortion2"],
        "reframed_thought": "Your empathetic reframe here."
    }}
    """
    try:
        response = llm_model.generate_content(prompt)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_text)
    except Exception:
        return {
            "distortions": ["General Stress"],
            "reframed_thought": "Take a deep breath. Focus on what is directly within your control right now."
        }

def generate_analytics_pdf(user_id: str) -> str:
    print(f"\n--> [DEBUG] Generating PDF for user {user_id}")
    
    entries_res = supabase.table("journal_entries").select("id").eq("user_id", user_id).execute()
    entries = entries_res.data
    total_entries = len(entries)
    
    if total_entries == 0:
        raise ValueError("No journal entries found to generate a report.")

    distortion_counts = {}
    for entry in entries:
        analysis_res = supabase.table("entry_analyses").select("distortions").eq("entry_id", entry["id"]).execute()
        if analysis_res.data:
            for distortion in analysis_res.data[0].get("distortions", []):
                distortion_counts[distortion] = distortion_counts.get(distortion, 0) + 1

    filename = f"CBT_Analytics_{user_id[:8]}.pdf"
    c = canvas.Canvas(filename)
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, "Cognitive Behavioral Analytics Report")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 770, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawString(50, 750, "-" * 60)
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 710, "Your Therapy Metrics:")
    
    c.setFont("Helvetica", 12)
    c.drawString(70, 680, f"Total Journal Entries Analyzed: {total_entries}")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 640, "Most Frequent Cognitive Distortions:")
    
    sorted_distortions = sorted(distortion_counts.items(), key=lambda x: x[1], reverse=True)
    y_position = 610
    c.setFont("Helvetica", 12)
    
    if not sorted_distortions:
        c.drawString(70, y_position, "No distortions detected yet. Great job!")
    else:
        for distortion, count in sorted_distortions:
            c.drawString(70, y_position, f"• {distortion}: Detected {count} times")
            y_position -= 25

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, max(y_position - 40, 50), "Use this data to identify triggers and practice reframing techniques.")

    c.save()
    print(f"--> [SUCCESS] PDF successfully written to {filename}")
    return filename

# ---------------------------------------------------------
# 4. API Endpoints
# ---------------------------------------------------------
@app.post("/api/journal/analyze", response_model=FullJournalResponse)
async def analyze_and_save_entry(entry: JournalInput, x_user_id: str = Header(...)):
    try:
        entry_res = supabase.table("journal_entries").insert({"user_id": x_user_id, "raw_text": entry.raw_text}).execute()
        saved_entry = entry_res.data[0]
        
        analysis = analyze_thought_with_llm(entry.raw_text)
        
        supabase.table("entry_analyses").insert({
            "entry_id": saved_entry["id"],
            "distortions": analysis["distortions"],
            "reframed_thought": analysis["reframed_thought"]
        }).execute()

        redis.delete(f"journal_entries:{x_user_id}")

        return {
            "entry_id": saved_entry["id"],
            "user_id": x_user_id,
            "raw_text": entry.raw_text,
            "distortions": analysis["distortions"],
            "reframed_thought": analysis["reframed_thought"],
            "created_at": saved_entry["created_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/journal", response_model=List[PastEntryResponse])
async def get_journal_entries(x_user_id: str = Header(...)):
    cache_key = f"journal_entries:{x_user_id}"
    cached_data = redis.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)

    try:
        response = supabase.table("journal_entries").select("*").eq("user_id", x_user_id).order("created_at", desc=True).execute()
        redis.set(cache_key, json.dumps(response.data), ex=3600)
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/journal/report")
async def request_pdf_report(x_user_id: str = Header(...)):
    try:
        filename = generate_analytics_pdf(x_user_id)
        return {
            "message": f"Your CBT PDF analytics report has been generated.",
            "filename": filename,
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))