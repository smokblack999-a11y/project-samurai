from fastapi import FastAPI
from pydantic import BaseModel, Field

from .openai_engine import analyze

app = FastAPI(title="Telegram LeadOps API", version="0.2.0")


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
    return {"status": "ok", "service": "telegram-leadops", "version": "0.2.0"}


@app.post("/api/v1/analyze/message", response_model=LeadDecision)
def analyze_message(req: AnalyzeRequest):
    return analyze(req.text)
