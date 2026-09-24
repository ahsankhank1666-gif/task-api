from pydantic import BaseModel, Field
from enum import Enum

# Define the closed lists of allowed values
class TicketCategory(str, Enum):
    BILLING = "billing"
    BUG = "bug"
    FEATURE = "feature"
    OTHER = "other"

class TicketUrgency(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

# Define the exact shape of the input we expect from the user[cite: 4]
class TriageInput(BaseModel):
    text: str = Field(..., max_length=2000)

# Define the exact shape of the output we expect from the AI[cite: 4]
class TriageOutput(BaseModel):
    category: TicketCategory
    urgency: TicketUrgency
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str