import time
from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import get_settings
from app.guardrails.input_guardrails import run_input_guardrails
from app.guardrails.output_guardrails import run_output_guardrails
from app.models import ChatRequest, ChatResponse
from app.services.audit import write_event
from app.services.llm_service import build_provider
from app.services.rate_limiter import InMemoryRateLimiter


settings = get_settings()

rate_limiter = InMemoryRateLimiter(
    max_requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)


def process_chat(request: ChatRequest) -> ChatResponse:
    request_id = str(uuid4())
    started = time.perf_counter()

    if not rate_limiter.allow(request.user_id):
        latency_ms = (time.perf_counter() - started) * 1000
        response = ChatResponse(
            status="blocked",
            answer=(
                "Rate limit exceeded. Wait briefly before submitting another "
                "request."
            ),
            safe_input="",
            input_checks=[],
            output_checks=[],
            provider=settings.llm_provider,
            model=settings.llm_model,
            latency_ms=round(latency_ms, 2),
            request_id=request_id,
        )
        _record_event(request, response)
        return response

    input_outcome = run_input_guardrails(request.message)

    if input_outcome.blocked:
        latency_ms = (time.perf_counter() - started) * 1000
        response = ChatResponse(
            status="blocked",
            answer=(
                "The request was blocked by the configured guardrails. Rephrase "
                "it as a legitimate, non-harmful business or educational question."
            ),
            safe_input=input_outcome.safe_text,
            input_checks=input_outcome.checks,
            output_checks=[],
            provider=settings.llm_provider,
            model=settings.llm_model,
            latency_ms=round(latency_ms, 2),
            request_id=request_id,
        )
        _record_event(request, response)
        return response

    provider = build_provider(settings)
    raw_answer = provider.generate(input_outcome.safe_text)
    output_outcome = run_output_guardrails(raw_answer)

    status = "rewritten" if output_outcome.rewritten else "allowed"
    latency_ms = (time.perf_counter() - started) * 1000

    response = ChatResponse(
        status=status,
        answer=output_outcome.safe_text,
        safe_input=input_outcome.safe_text,
        input_checks=input_outcome.checks,
        output_checks=output_outcome.checks,
        provider=settings.llm_provider,
        model=settings.llm_model,
        latency_ms=round(latency_ms, 2),
        request_id=request_id,
    )
    _record_event(request, response)
    return response


def _record_event(request: ChatRequest, response: ChatResponse) -> None:
    pii_detected = any(
        check.name == "pii_redaction" and check.decision == "redact"
        for check in response.input_checks
    )
    injection_detected = any(
        check.name == "prompt_injection" and not check.passed
        for check in response.input_checks
    )
    secret_detected = any(
        check.name == "secret_redaction" and check.decision == "redact"
        for check in response.input_checks
    )

    write_event(
        settings.audit_file,
        {
            "request_id": response.request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": request.session_id,
            "user_id": request.user_id,
            "status": response.status,
            "provider": response.provider,
            "model": response.model,
            "latency_ms": response.latency_ms,
            "pii_detected": pii_detected,
            "injection_detected": injection_detected,
            "secret_detected": secret_detected,
        },
    )
