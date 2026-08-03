from fastapi import FastAPI

from app.core.config import get_settings
from app.evaluation import run_evaluation
from app.models import (
    ChatRequest,
    ChatResponse,
    EvaluationResponse,
    StatsResponse,
)
from app.services.audit import read_events, summarize_events
from app.services.pipeline import process_chat


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Standalone GenAI guardrails platform with prompt-injection blocking, "
        "PII and secret redaction, restricted-content controls, output validation, "
        "rate limiting, audit logging, evaluation, and provider abstraction."
    ),
)


@app.get("/")
def root() -> dict:
    return {
        "message": settings.app_name,
        "docs": "/docs",
        "dashboard_command": "streamlit run dashboard.py",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "healthy",
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "environment": settings.environment,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return process_chat(request)


@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate() -> EvaluationResponse:
    return run_evaluation()


@app.get("/guardrail-stats", response_model=StatsResponse)
def guardrail_stats() -> StatsResponse:
    return summarize_events(read_events(settings.audit_file))
