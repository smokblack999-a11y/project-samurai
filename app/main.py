from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Telegram LeadOps API", version="0.1.0")

class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    language: str | None = None

class LeadDecision(BaseModel):
    intent: str
    lead_score: int = Field(ge=0, le=100)
    urgency: str
    recommended_action: str
    needs: list[str]
    reason: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "telegram-leadops"}

@app.post("/api/v1/analyze/message", response_model=LeadDecision)
def analyze_message(req: AnalyzeRequest):
    text = req.text.lower()
    buying_terms = ("купить", "цена", "стоимость", "заказать", "сколько стоит")
    is_buying = any(term in text for term in buying_terms)
    return LeadDecision(
        intent="buying" if is_buying else "information",
        lead_score=85 if is_buying else 35,
        urgency="high" if is_buying else "low",
        recommended_action="human_followup" if is_buying else "auto_reply",
        needs=["price"] if is_buying else [],
        reason="Detected explicit purchase intent" if is_buying else "No explicit purchase intent detected",
    )
