from apps.ai_engine.fallback_rules import rule_based_ticket_classification
from apps.ai_engine.llm_provider import LLMProvider, LLMProviderError, extract_json_from_text
from apps.ai_engine.prompt_templates import (
    TICKET_CLASSIFICATION_SYSTEM_PROMPT,
    build_ticket_classification_prompt,
)


ALLOWED_REQUEST_TYPES = ["IT", "HR", "FACILITIES"]
ALLOWED_PRIORITIES = ["HIGH", "MEDIUM", "LOW"]
ALLOWED_SENTIMENTS = [
    "CALM",
    "CONFUSED",
    "FRUSTRATED",
    "ANGRY",
    "URGENT",
    "NEUTRAL",
]


def safe_bool(value) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() in ["true", "yes", "1"]

    return False


def safe_float(value, default: float = 0.75) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return default

    if value < 0:
        return 0.0

    if value > 1:
        return 1.0

    return value


def clean_classification(data: dict, fallback: dict, model_used: str) -> dict:
    request_type = str(data.get("request_type", fallback["request_type"])).upper()
    priority = str(data.get("priority", fallback["priority"])).upper()
    sentiment = str(data.get("sentiment", fallback["sentiment"])).upper()

    if request_type not in ALLOWED_REQUEST_TYPES:
        request_type = fallback["request_type"]

    if priority not in ALLOWED_PRIORITIES:
        priority = fallback["priority"]

    if sentiment not in ALLOWED_SENTIMENTS:
        sentiment = fallback["sentiment"]

    summary = str(data.get("summary", fallback["summary"])).strip()
    suggested_solution = str(
        data.get("suggested_solution", fallback["suggested_solution"])
    ).strip()

    reason = str(data.get("reason", "Classified using LLM provider.")).strip()

    escalation_required = safe_bool(
        data.get("escalation_required", fallback["escalation_required"])
    )

    confidence_score = safe_float(
        data.get("confidence_score", fallback["confidence_score"]),
        default=fallback["confidence_score"],
    )

    if not summary:
        summary = fallback["summary"]

    if not suggested_solution:
        suggested_solution = fallback["suggested_solution"]

    if priority == "HIGH" or sentiment in ["URGENT", "ANGRY"]:
        escalation_required = True

    return {
        "request_type": request_type,
        "priority": priority,
        "sentiment": sentiment,
        "summary": summary,
        "suggested_solution": suggested_solution,
        "escalation_required": escalation_required,
        "confidence_score": confidence_score,
        "reason": reason,
        "model_used": model_used,
    }


def classify_ticket(subject: str, description: str) -> dict:
    fallback = rule_based_ticket_classification(subject, description)

    provider = LLMProvider()

    try:
        response_text, model_used = provider.generate_text(
            system_prompt=TICKET_CLASSIFICATION_SYSTEM_PROMPT,
            user_prompt=build_ticket_classification_prompt(subject, description),
        )

        llm_data = extract_json_from_text(response_text)

        return clean_classification(
            data=llm_data,
            fallback=fallback,
            model_used=model_used,
        )

    except (LLMProviderError, ValueError, KeyError, TypeError):
        return fallback