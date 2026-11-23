from fastapi import FastAPI, HTTPException
from .models import AnalyzeMessageRequest, LeadDecision
from .ai import analyze

app = FastAPI(title="Telegram LeadOps AI", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "online", "service": "telegram-leadops-api", "version": app.version}

@app.post("/api/v1/analyze/message", response_model=LeadDecision)
def analyze_message(req: AnalyzeMessageRequest):
    try:
        return analyze(req)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=502, detail="AI provider request failed")
