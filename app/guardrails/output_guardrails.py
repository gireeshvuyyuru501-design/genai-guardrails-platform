import re
from dataclasses import dataclass

from app.models import GuardrailCheck


UNSAFE_OUTPUT_PATTERNS = [
    r"system prompt\s*:",
    r"developer message\s*:",
    r"hidden instructions\s*:",
    r"here is how to build a bomb",
    r"here is ransomware code",
]

OUTPUT_SECRET_PATTERNS = [
    re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
]

DISCLAIMER = (
    "AI-generated response: verify important information before using it "
    "for legal, financial, medical, security, or other high-impact decisions."
)


@dataclass
class OutputOutcome:
    safe_text: str
    rewritten: bool
    checks: list[GuardrailCheck]


def run_output_guardrails(text: str) -> OutputOutcome:
    cleaned = text.strip()
    checks: list[GuardrailCheck] = []
    rewritten = False

    unsafe_found = any(
        re.search(pattern, cleaned, flags=re.IGNORECASE)
        for pattern in UNSAFE_OUTPUT_PATTERNS
    )
    checks.append(
        GuardrailCheck(
            name="unsafe_output",
            passed=not unsafe_found,
            decision="rewrite" if unsafe_found else "allow",
            severity="critical" if unsafe_found else "info",
            details=(
                "Unsafe output pattern detected."
                if unsafe_found
                else "No unsafe output pattern detected."
            ),
        )
    )

    if unsafe_found:
        cleaned = (
            "I can’t provide that content. I can help with a safe, defensive, "
            "or high-level alternative."
        )
        rewritten = True

    secret_found = False
    for pattern in OUTPUT_SECRET_PATTERNS:
        if pattern.search(cleaned):
            secret_found = True
            cleaned = pattern.sub("[REDACTED_SECRET]", cleaned)

    checks.append(
        GuardrailCheck(
            name="output_secret_filter",
            passed=not secret_found,
            decision="rewrite" if secret_found else "allow",
            severity="critical" if secret_found else "info",
            details=(
                "Secret-like value removed from output."
                if secret_found
                else "No secret-like value detected in output."
            ),
        )
    )
    rewritten = rewritten or secret_found

    minimum_quality = len(cleaned) >= 40
    checks.append(
        GuardrailCheck(
            name="minimum_quality",
            passed=minimum_quality,
            decision="rewrite" if not minimum_quality else "allow",
            severity="medium" if not minimum_quality else "info",
            details=(
                "Output meets the minimum quality threshold."
                if minimum_quality
                else "Output was too short and required a safe fallback."
            ),
        )
    )
    if not minimum_quality:
        cleaned = (
            "I’m unable to produce a sufficiently complete answer. Please add "
            "more context so I can respond safely and accurately."
        )
        rewritten = True

    has_disclaimer = DISCLAIMER in cleaned
    if not has_disclaimer:
        cleaned = f"{cleaned}\n\n{DISCLAIMER}"
        rewritten = True

    checks.append(
        GuardrailCheck(
            name="high_impact_disclaimer",
            passed=True,
            decision="rewrite" if not has_disclaimer else "allow",
            severity="low",
            details=(
                "High-impact disclaimer appended."
                if not has_disclaimer
                else "High-impact disclaimer already present."
            ),
        )
    )

    return OutputOutcome(
        safe_text=cleaned,
        rewritten=rewritten,
        checks=checks,
    )
