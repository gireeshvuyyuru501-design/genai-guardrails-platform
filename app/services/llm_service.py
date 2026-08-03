from abc import ABC, abstractmethod

from app.core.config import Settings


class Provider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class MockProvider(Provider):
    """Deterministic provider for an API-key-free portfolio demo."""

    def generate(self, prompt: str) -> str:
        lowered = prompt.lower()

        if "guardrail" in lowered:
            return (
                "GenAI guardrails are safety and quality controls placed before and "
                "after a model call. Input controls detect prompt injection, personal "
                "information, credentials, toxicity, and restricted requests. Output "
                "controls detect unsafe content, secret leakage, weak answers, and "
                "missing high-impact disclaimers."
            )

        if "rag" in lowered:
            return (
                "Retrieval-augmented generation combines document retrieval with text "
                "generation. A retriever selects relevant context, and the generation "
                "component uses that context to create a grounded answer. Guardrails "
                "can enforce access control, citation requirements, and refusal when "
                "context is insufficient."
            )

        return (
            "The request passed the configured input guardrails. This deterministic "
            "local response demonstrates the complete safety pipeline without requiring "
            "OpenAI, Anthropic, Gemini, or any paid API key."
        )


def build_provider(settings: Settings) -> Provider:
    if settings.llm_provider.strip().lower() != "mock":
        raise ValueError(
            "This build uses LLM_PROVIDER=mock and requires no external API key."
        )
    return MockProvider()
