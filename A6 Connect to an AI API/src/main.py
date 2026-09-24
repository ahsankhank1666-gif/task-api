import os
import json
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from src.llm.schema import TriageInput, TriageOutput, TicketCategory, TicketUrgency

load_dotenv()

app = FastAPI()

# Stage 4: Strict 30s timeout and default retry policy for 429/5xx errors
client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    timeout=30.0,
    max_retries=2
)

def load_prompt() -> str:
    return Path("prompts/triage-v1.md").read_text(encoding="utf-8")

def log_cost(tokens: int, duration: float, repaired: bool):
    os.makedirs("logs", exist_ok=True)
    with open("logs/costs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "model": os.environ["LLM_MODEL"],
            "total_tokens": tokens,
            "duration_ms": round(duration * 1000, 2),
            "repaired": repaired
        }) + "\n")

@app.post("/triage", response_model=TriageOutput)
async def triage_ticket(request: TriageInput):
    # Stage 4: Kill Switch
    if os.getenv("LLM_ENABLED", "true").lower() == "false":
        return TriageOutput(category=TicketCategory.OTHER, urgency=TicketUrgency.NORMAL, confidence=1.0, reason="Kill switch active.")
    
    if os.getenv("LLM_STUB") == "1":
        return TriageOutput(category=TicketCategory.BILLING, urgency=TicketUrgency.HIGH, confidence=0.95, reason="STUB MODE")
    
    messages = [
        {"role": "system", "content": load_prompt()},
        {"role": "user", "content": request.text}
    ]

    start_time = time.time()
    response = client.chat.completions.create(model=os.environ["LLM_MODEL"], temperature=0.2, messages=messages)
    raw_content = response.choices[0].message.content.strip()
    
    # Strip markdown code fences if the model added them
    if raw_content.startswith("```json"):
        raw_content = raw_content.strip("`").replace("json\n", "", 1)
        
    try:
        data = json.loads(raw_content)
        validated_data = TriageOutput(**data)
        log_cost(response.usage.total_tokens, time.time() - start_time, False)
        return validated_data
        
    except (json.JSONDecodeError, ValidationError) as e:
        # Stage 3: The Repair Loop
        messages.append({"role": "assistant", "content": raw_content})
        messages.append({"role": "user", "content": f"Your previous answer was rejected: {str(e)}. Return only corrected JSON matching the schema."})
        
        repair_response = client.chat.completions.create(model=os.environ["LLM_MODEL"], temperature=0.2, messages=messages)
        repair_content = repair_response.choices[0].message.content.strip()
        
        if repair_content.startswith("```json"):
            repair_content = repair_content.strip("`").replace("json\n", "", 1)
            
        try:
            repair_data = json.loads(repair_content)
            validated_repair = TriageOutput(**repair_data)
            log_cost(response.usage.total_tokens + repair_response.usage.total_tokens, time.time() - start_time, True)
            return validated_repair
            
        except Exception:
            # Stage 3: Quarantine on total failure
            os.makedirs("logs", exist_ok=True)
            with open("logs/quarantine.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({"input": request.text, "error": str(e), "raw": repair_content}) + "\n")
            raise HTTPException(status_code=422, detail="Unprocessable AI response logged to quarantine.")