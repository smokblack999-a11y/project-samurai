from fastapi import FastAPI
from pydantic import BaseModel

from .evaluation import run_evaluation
from .metrics import metrics
from .openai_engine import analyze
from .schemas import AnalyzeRequest, LeadDecision, NormalizedMessage

app = FastAPI(title="Telegram LeadOps API", version="0.3.0")


class IngestResponse(BaseModel):
    accepted: bool
    decision: LeadDecision


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "telegram-leadops",
        "version": "0.3.0",
    }


@app.get("/api/v1/system/status")
def system_status():
    return {
        "service": "telegram-leadops",
        "version": "0.3.0",
        "status": "ok",
        "telegram": {"connected": False, "adapter": "normalized-event-ready"},
        "ai": {"configured": bool(__import__("os").getenv("OPENAI_API_KEY"))},
        "metrics": metrics.snapshot(),
    }


@app.post("/api/v1/analyze/message", response_model=LeadDecision)
def analyze_message(req: AnalyzeRequest):
    metrics.inc("analysis_requests")
    decision = LeadDecision.model_validate(analyze(req.text))
    metrics.inc(f"intent_{decision.intent}")
    metrics.inc(f"action_{decision.recommended_action}")
    return decision


@app.post("/api/v1/ingest/telegram", response_model=IngestResponse)
def ingest_telegram(message: NormalizedMessage):
    metrics.inc("telegram_events")
    decision = LeadDecision.model_validate(analyze(message.text))
    metrics.inc(f"intent_{decision.intent}")
    return IngestResponse(accepted=True, decision=decision)


@app.get("/api/v1/evaluation")
def evaluation():
    return run_evaluation()
