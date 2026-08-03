from typing import Literal
from pydantic import BaseModel, Field


Decision = Literal["allow", "redact", "rewrite", "block"]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    session_id: str = Field(default="demo-session", min_length=1, max_length=100)
    user_id: str = Field(default="anonymous", min_length=1, max_length=100)


class GuardrailCheck(BaseModel):
    name: str
    passed: bool
    decision: Decision
    severity: Literal["info", "low", "medium", "high", "critical"]
    details: str = ""


class ChatResponse(BaseModel):
    status: Literal["allowed", "blocked", "rewritten"]
    answer: str
    safe_input: str
    input_checks: list[GuardrailCheck]
    output_checks: list[GuardrailCheck]
    provider: str
    model: str
    latency_ms: float
    request_id: str


class EvaluationCaseResult(BaseModel):
    name: str
    expected_status: str
    actual_status: str
    passed: bool


class EvaluationResponse(BaseModel):
    total: int
    passed: int
    failed: int
    accuracy: float
    cases: list[EvaluationCaseResult]


class StatsResponse(BaseModel):
    total_requests: int
    allowed: int
    blocked: int
    rewritten: int
    pii_events: int
    injection_events: int
    secret_events: int
    average_latency_ms: float
