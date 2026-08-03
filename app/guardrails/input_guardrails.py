import re
from dataclasses import dataclass

from app.models import GuardrailCheck


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(me\s+)?your\s+hidden\s+instructions",
    r"print\s+(the\s+)?developer\s+message",
    r"jailbreak",
    r"do\s+anything\s+now",
    r"override\s+(the\s+)?safety",
]

RESTRICTED_PATTERNS = [
    r"\b(?:make|build)\s+(?:a\s+)?bomb\b",
    r"\b(?:make|build)\s+(?:a\s+)?weapon\b",
    
    
    r"\bsteal\s+(a\s+)?password\b",
    r"\bwrite\s+(a\s+)?ransomware\b",
    r"\bdeploy\s+(a\s+)?keylogger\b",
]

SECRET_PATTERNS = {
    "openai_key": re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}\b"),
    "anthropic_key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
}

PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
}

TOXIC_TERMS = {
    "idiot",
    "moron",
    "stupid",
}


@dataclass
class InputOutcome:
    safe_text: str
    blocked: bool
    checks: list[GuardrailCheck]


def run_input_guardrails(text: str) -> InputOutcome:
    normalized = text.strip()
    lowered = normalized.lower()
    checks: list[GuardrailCheck] = []

    injection_found = any(
        re.search(pattern, lowered, flags=re.IGNORECASE)
        for pattern in PROMPT_INJECTION_PATTERNS
    )
    checks.append(
        GuardrailCheck(
            name="prompt_injection",
            passed=not injection_found,
            decision="block" if injection_found else "allow",
            severity="critical" if injection_found else "info",
            details=(
                "Prompt-injection or jailbreak language detected."
                if injection_found
                else "No configured prompt-injection pattern detected."
            ),
        )
    )

    restricted_found = any(
        re.search(pattern, lowered, flags=re.IGNORECASE)
        for pattern in RESTRICTED_PATTERNS
    )
    checks.append(
        GuardrailCheck(
            name="restricted_content",
            passed=not restricted_found,
            decision="block" if restricted_found else "allow",
            severity="critical" if restricted_found else "info",
            details=(
                "Restricted harmful request detected."
                if restricted_found
                else "No restricted-content pattern detected."
            ),
        )
    )

    safe_text = normalized
    pii_types: list[str] = []
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(safe_text):
            pii_types.append(pii_type)
            safe_text = pattern.sub(f"[REDACTED_{pii_type.upper()}]", safe_text)

    checks.append(
        GuardrailCheck(
            name="pii_redaction",
            passed=True,
            decision="redact" if pii_types else "allow",
            severity="high" if pii_types else "info",
            details=(
                f"Redacted PII types: {', '.join(pii_types)}."
                if pii_types
                else "No configured PII detected."
            ),
        )
    )

    secret_types: list[str] = []
    for secret_type, pattern in SECRET_PATTERNS.items():
        if pattern.search(safe_text):
            secret_types.append(secret_type)
            safe_text = pattern.sub(f"[REDACTED_{secret_type.upper()}]", safe_text)

    checks.append(
        GuardrailCheck(
            name="secret_redaction",
            passed=True,
            decision="redact" if secret_types else "allow",
            severity="critical" if secret_types else "info",
            details=(
                f"Redacted secret types: {', '.join(secret_types)}."
                if secret_types
                else "No configured secrets detected."
            ),
        )
    )

    toxic_found = sorted(term for term in TOXIC_TERMS if term in lowered)
    checks.append(
        GuardrailCheck(
            name="toxicity",
            passed=not bool(toxic_found),
            decision="rewrite" if toxic_found else "allow",
            severity="medium" if toxic_found else "info",
            details=(
                f"Detected toxic terms: {', '.join(toxic_found)}."
                if toxic_found
                else "No configured toxic terms detected."
            ),
        )
    )

    return InputOutcome(
        safe_text=safe_text,
        blocked=injection_found or restricted_found,
        checks=checks,
    )

