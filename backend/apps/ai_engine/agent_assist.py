from django.db.models import Q

from apps.ai_engine.llm_provider import LLMProvider, LLMProviderError, extract_json_from_text
from apps.ai_engine.prompt_templates import (
    AGENT_ASSIST_SYSTEM_PROMPT,
    build_agent_assist_prompt,
)
from apps.tickets.models import Ticket


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


def build_ticket_context(ticket: Ticket) -> str:
    message_lines = []

    for message in ticket.messages.all().order_by("created_at"):
        sender = message.sender_role
        message_lines.append(f"{sender}: {message.message}")

    attachment_lines = []

    for attachment in ticket.attachments.all().order_by("-uploaded_at"):
        if attachment.analysis_result:
            attachment_lines.append(
                f"{attachment.file_type} attachment analysis: {attachment.analysis_result}"
            )

    return f"""
Ticket ID: {ticket.id}
Subject: {ticket.subject}
Description: {ticket.description}
Request Type: {ticket.request_type}
Priority: {ticket.priority}
Status: {ticket.status}
Sentiment: {ticket.sentiment}
AI Summary: {ticket.ai_summary}
AI Suggested Solution: {ticket.ai_suggested_solution}
Escalation Required: {ticket.escalation_required}

Conversation Thread:
{chr(10).join(message_lines) if message_lines else "No messages yet."}

Attachment Analysis:
{chr(10).join(attachment_lines) if attachment_lines else "No analyzed attachments."}
"""


def get_priority_reason(ticket: Ticket) -> str:
    if ticket.priority == Ticket.Priority.HIGH:
        if ticket.escalation_required:
            return (
                "This ticket is marked HIGH because it appears to block user work "
                "or needs urgent attention. Escalation is recommended."
            )
        return "This ticket is marked HIGH because the issue may strongly affect business work."

    if ticket.priority == Ticket.Priority.MEDIUM:
        return (
            "This ticket is marked MEDIUM because the issue affects the user, "
            "but it does not clearly show complete work stoppage."
        )

    return "This ticket is marked LOW because it appears to be a general or non-urgent request."


def get_sentiment_explanation(ticket: Ticket) -> str:
    explanations = {
        Ticket.Sentiment.URGENT: (
            "The user message indicates urgency, possibly because work is blocked "
            "or there is a time-sensitive business need."
        ),
        Ticket.Sentiment.ANGRY: (
            "The user appears angry or highly dissatisfied. The agent should respond "
            "with empathy and quick ownership."
        ),
        Ticket.Sentiment.FRUSTRATED: (
            "The user appears frustrated. The agent should acknowledge the inconvenience "
            "and provide clear next steps."
        ),
        Ticket.Sentiment.CONFUSED: (
            "The user seems unsure about the issue or process. The agent should provide "
            "simple step-by-step guidance."
        ),
        Ticket.Sentiment.CALM: (
            "The user tone appears calm. A clear and professional response is suitable."
        ),
        Ticket.Sentiment.NEUTRAL: (
            "The user tone appears neutral. The agent can respond with direct troubleshooting steps."
        ),
    }

    return explanations.get(ticket.sentiment, "User sentiment is not clearly identified.")


def find_related_kb_articles(ticket: Ticket, limit: int = 3) -> list[dict]:
    try:
        from apps.knowledge_base.embeddings import generate_embedding
        from apps.knowledge_base.vector_store import VectorStoreService

        query = f"{ticket.subject}. {ticket.description}. {ticket.ai_summary}"
        query_embedding = generate_embedding(query)

        vector_store = VectorStoreService()
        results = vector_store.search(
            query_embedding=query_embedding,
            top_k=limit,
        )

        articles = []

        for item in results:
            metadata = item.get("metadata", {})
            score = item.get("similarity_score", 0.0)

            if score <= 0:
                continue

            articles.append(
                {
                    "document_id": metadata.get("document_id"),
                    "document_title": metadata.get("document_title"),
                    "file_name": metadata.get("file_name"),
                    "chunk_index": metadata.get("chunk_index"),
                    "similarity_score": round(score, 4),
                    "preview": item.get("text", "")[:300],
                }
            )

        return articles

    except Exception:
        return []


def find_similar_tickets(ticket: Ticket, limit: int = 5) -> list[dict]:
    keywords = []

    for part in [ticket.subject, ticket.description, ticket.ai_summary]:
        for word in part.lower().split():
            word = word.strip(".,!?;:()[]{}")
            if len(word) >= 5:
                keywords.append(word)

    keywords = list(dict.fromkeys(keywords))[:8]

    query_filter = Q()

    for word in keywords:
        query_filter |= Q(subject__icontains=word)
        query_filter |= Q(description__icontains=word)
        query_filter |= Q(ai_summary__icontains=word)

    queryset = Ticket.objects.exclude(id=ticket.id)

    if ticket.request_type:
        queryset = queryset.filter(request_type=ticket.request_type)

    if query_filter:
        queryset = queryset.filter(query_filter)

    queryset = queryset.order_by("-created_at")[:limit]

    similar = []

    for item in queryset:
        similar.append(
            {
                "id": item.id,
                "subject": item.subject,
                "request_type": item.request_type,
                "priority": item.priority,
                "status": item.status,
                "sentiment": item.sentiment,
                "ai_summary": item.ai_summary,
                "ai_suggested_solution": item.ai_suggested_solution,
                "created_at": item.created_at.isoformat(),
            }
        )

    return similar


def build_kb_context(related_kb_articles: list[dict]) -> str:
    if not related_kb_articles:
        return "No related knowledge base articles found."

    lines = []

    for index, article in enumerate(related_kb_articles, start=1):
        lines.append(
            f"KB Article {index}: {article.get('document_title')}\n"
            f"Preview: {article.get('preview')}"
        )

    return "\n\n".join(lines)


def build_similar_ticket_context(similar_tickets: list[dict]) -> str:
    if not similar_tickets:
        return "No similar past tickets found."

    lines = []

    for index, ticket in enumerate(similar_tickets, start=1):
        lines.append(
            f"Similar Ticket {index}: #{ticket.get('id')} - {ticket.get('subject')}\n"
            f"Status: {ticket.get('status')}\n"
            f"Previous suggested solution: {ticket.get('ai_suggested_solution')}"
        )

    return "\n\n".join(lines)


def fallback_agent_assist(ticket: Ticket, related_kb_articles: list[dict], similar_tickets: list[dict]) -> dict:
    ticket_summary = ticket.ai_summary or f"{ticket.subject} - {ticket.description[:160]}"

    priority_reason = get_priority_reason(ticket)
    sentiment_explanation = get_sentiment_explanation(ticket)

    if ticket.ai_suggested_solution:
        suggested_steps = ticket.ai_suggested_solution
    elif related_kb_articles:
        suggested_steps = related_kb_articles[0].get("preview", "")
    else:
        suggested_steps = (
            "1. Acknowledge the issue.\n"
            "2. Ask for required details such as screenshot, device name, location, or error message.\n"
            "3. Provide first-level troubleshooting steps.\n"
            "4. Escalate if the issue blocks work or needs specialist support."
        )

    if ticket.priority == Ticket.Priority.HIGH or ticket.escalation_required:
        escalation_suggestion = (
            "Escalation is recommended because the ticket is high priority or marked as escalation required."
        )
    else:
        escalation_suggestion = (
            "Escalation is not immediately required. Handle with standard support process first."
        )

    suggested_reply = (
        "Hi, thank you for sharing the details. I understand the issue you are facing. "
        "Please try the suggested steps below and share any screenshot or error message if the issue continues. "
        "I will monitor this ticket and escalate it if required."
    )

    if ticket.request_type == Ticket.RequestType.IT:
        suggested_reply = (
            "Hi, thank you for reporting this issue. I understand this is affecting your system usage. "
            "Please try the initial troubleshooting steps and share a screenshot/error message if the issue still continues. "
            "I will check and escalate to the IT support team if needed."
        )

    elif ticket.request_type == Ticket.RequestType.HR:
        suggested_reply = (
            "Hi, thank you for reaching out. I will review your HR-related request. "
            "Please share your employee ID and any relevant month/date or document details so we can process it correctly."
        )

    elif ticket.request_type == Ticket.RequestType.FACILITIES:
        suggested_reply = (
            "Hi, thank you for reporting this facilities issue. Please share your floor, seat/location details, "
            "and a photo if applicable. I will coordinate with the facilities team."
        )

    return {
        "ticket_summary": ticket_summary,
        "priority_reason": priority_reason,
        "sentiment_explanation": sentiment_explanation,
        "suggested_reply": suggested_reply,
        "suggested_steps": suggested_steps,
        "escalation_suggestion": escalation_suggestion,
        "related_kb_articles": related_kb_articles,
        "similar_tickets": similar_tickets,
        "model_used": "agent-assist-fallback",
        "confidence_score": 0.72,
    }


def clean_agent_assist_data(
    data: dict,
    fallback: dict,
    related_kb_articles: list[dict],
    similar_tickets: list[dict],
    model_used: str,
) -> dict:
    return {
        "ticket_summary": str(
            data.get("ticket_summary", fallback["ticket_summary"])
        ).strip(),
        "priority_reason": str(
            data.get("priority_reason", fallback["priority_reason"])
        ).strip(),
        "sentiment_explanation": str(
            data.get("sentiment_explanation", fallback["sentiment_explanation"])
        ).strip(),
        "suggested_reply": str(
            data.get("suggested_reply", fallback["suggested_reply"])
        ).strip(),
        "suggested_steps": str(
            data.get("suggested_steps", fallback["suggested_steps"])
        ).strip(),
        "escalation_suggestion": str(
            data.get("escalation_suggestion", fallback["escalation_suggestion"])
        ).strip(),
        "related_kb_articles": related_kb_articles,
        "similar_tickets": similar_tickets,
        "model_used": model_used,
        "confidence_score": safe_float(
            data.get("confidence_score", fallback["confidence_score"]),
            fallback["confidence_score"],
        ),
    }


def generate_agent_assist(ticket: Ticket) -> dict:
    related_kb_articles = find_related_kb_articles(ticket)
    similar_tickets = find_similar_tickets(ticket)

    fallback = fallback_agent_assist(
        ticket=ticket,
        related_kb_articles=related_kb_articles,
        similar_tickets=similar_tickets,
    )

    provider = LLMProvider()

    try:
        response_text, model_used = provider.generate_text(
            system_prompt=AGENT_ASSIST_SYSTEM_PROMPT,
            user_prompt=build_agent_assist_prompt(
                ticket_context=build_ticket_context(ticket),
                kb_context=build_kb_context(related_kb_articles),
                similar_context=build_similar_ticket_context(similar_tickets),
            ),
        )

        data = extract_json_from_text(response_text)

        cleaned = clean_agent_assist_data(
            data=data,
            fallback=fallback,
            related_kb_articles=related_kb_articles,
            similar_tickets=similar_tickets,
            model_used=model_used,
        )

        if not cleaned["suggested_reply"]:
            return fallback

        return cleaned

    except (LLMProviderError, ValueError, KeyError, TypeError):
        return fallback