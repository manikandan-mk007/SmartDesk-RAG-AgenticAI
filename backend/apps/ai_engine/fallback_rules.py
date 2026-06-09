import re


def normalize_text(subject: str, description: str) -> str:
    return f"{subject} {description}".lower().strip()


def contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def classify_request_type(text: str) -> str:
    it_keywords = [
        "laptop",
        "system",
        "computer",
        "desktop",
        "monitor",
        "keyboard",
        "mouse",
        "wifi",
        "wi-fi",
        "internet",
        "network",
        "vpn",
        "password",
        "login",
        "account locked",
        "email",
        "outlook",
        "teams",
        "printer",
        "software",
        "install",
        "windows",
        "blue screen",
        "bsod",
        "slow",
        "crash",
        "battery",
        "charger",
        "server",
        "application",
        "access issue",
    ]

    hr_keywords = [
        "payslip",
        "salary",
        "payroll",
        "leave",
        "attendance",
        "holiday",
        "onboarding",
        "exit",
        "resignation",
        "employee id",
        "hr policy",
        "policy",
        "benefits",
        "reimbursement",
        "increment",
        "offer letter",
        "experience letter",
    ]

    facilities_keywords = [
        "ac",
        "air conditioner",
        "chair",
        "desk",
        "seat",
        "seating",
        "meeting room",
        "parking",
        "cafeteria",
        "canteen",
        "housekeeping",
        "cleaning",
        "access card",
        "id card",
        "door",
        "light",
        "fan",
        "power",
        "water",
        "washroom",
        "facility",
        "facilities",
    ]

    if contains_any(text, hr_keywords):
        return "HR"

    if contains_any(text, facilities_keywords):
        return "FACILITIES"

    if contains_any(text, it_keywords):
        return "IT"

    return "IT"


def classify_sentiment(text: str) -> str:
    urgent_keywords = [
        "urgent",
        "immediately",
        "client meeting",
        "meeting today",
        "production",
        "blocked",
        "not able to work",
        "cannot work",
        "deadline",
        "critical",
        "asap",
        "emergency",
    ]

    angry_keywords = [
        "angry",
        "very bad",
        "worst",
        "frustrated",
        "not acceptable",
        "again and again",
        "fed up",
    ]

    confused_keywords = [
        "confused",
        "not sure",
        "don't know",
        "dont know",
        "unable to understand",
        "how to",
        "help me",
    ]

    if contains_any(text, urgent_keywords):
        return "URGENT"

    if contains_any(text, angry_keywords):
        return "ANGRY"

    if contains_any(text, confused_keywords):
        return "CONFUSED"

    if "please" in text or "kindly" in text:
        return "CALM"

    return "NEUTRAL"


def classify_priority(text: str, request_type: str, sentiment: str) -> str:
    high_keywords = [
        "urgent",
        "immediately",
        "client meeting",
        "meeting today",
        "production",
        "blocked",
        "not able to work",
        "cannot work",
        "system down",
        "not turning on",
        "account locked",
        "security",
        "critical",
        "deadline",
        "asap",
        "emergency",
    ]

    low_keywords = [
        "request",
        "general",
        "information",
        "when possible",
        "not urgent",
        "minor",
        "query",
    ]

    if sentiment in ["URGENT", "ANGRY"]:
        return "HIGH"

    if contains_any(text, high_keywords):
        return "HIGH"

    if contains_any(text, low_keywords):
        return "LOW"

    if request_type in ["IT", "HR", "FACILITIES"]:
        return "MEDIUM"

    return "MEDIUM"


def build_summary(subject: str, description: str) -> str:
    description = re.sub(r"\s+", " ", description).strip()

    if len(description) > 140:
        description = description[:140].rstrip() + "..."

    return f"{subject.strip()} - {description}"


def build_suggested_solution(request_type: str, text: str) -> str:
    if request_type == "IT":
        if "password" in text or "account locked" in text or "login" in text:
            return (
                "Ask the user to verify credentials, try password reset, clear browser cache, "
                "and share any error screenshot if login still fails."
            )

        if "vpn" in text:
            return (
                "Ask the user to check internet connection, restart VPN client, verify credentials, "
                "and retry. If the error continues, collect screenshot and escalate to IT network support."
            )

        if "laptop" in text or "system" in text or "not turning on" in text:
            return (
                "Ask the user to connect charger, check power indicator, hold power button for 15 seconds, "
                "try another power socket, and share device details. Escalate if still not working."
            )

        if "teams" in text or "outlook" in text:
            return (
                "Ask the user to restart the application, check internet connection, clear app cache, "
                "and login again. Escalate if the issue continues."
            )

        return (
            "Collect error details, screenshot, device information, and recent changes. "
            "Guide the user with basic restart, network check, and application retry steps."
        )

    if request_type == "HR":
        return (
            "Ask the user to provide employee ID, relevant date/month, and issue details. "
            "Forward to HR team if policy, payroll, attendance, or document correction is required."
        )

    if request_type == "FACILITIES":
        return (
            "Ask the user to provide location, floor, seat number, and photo if applicable. "
            "Forward to facilities team for physical inspection or service action."
        )

    return "Collect more details from the user and assign the ticket to the correct support team."


def rule_based_ticket_classification(subject: str, description: str) -> dict:
    text = normalize_text(subject, description)

    request_type = classify_request_type(text)
    sentiment = classify_sentiment(text)
    priority = classify_priority(text, request_type, sentiment)

    escalation_required = priority == "HIGH" or sentiment in ["URGENT", "ANGRY"]

    return {
        "request_type": request_type,
        "priority": priority,
        "sentiment": sentiment,
        "summary": build_summary(subject, description),
        "suggested_solution": build_suggested_solution(request_type, text),
        "escalation_required": escalation_required,
        "confidence_score": 0.70,
        "reason": "Classified using local rule-based fallback.",
        "model_used": "rule-based-fallback",
    }