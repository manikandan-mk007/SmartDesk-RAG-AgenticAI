import re

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole, IsUserRole
from apps.tickets.models import Ticket, TicketActivityLog, TicketMessage

from .models import KBDocument
from .rag_service import ask_rag
from .serializers import (
    CreateTicketFromRAGSerializer,
    KBDocumentSerializer,
    KBDocumentUploadSerializer,
    RAGAskSerializer,
)
from .services import process_kb_document
from .vector_store import VectorStoreService


FOLLOW_UP_KEYWORDS = [
    "not working",
    "still same",
    "still not",
    "not fixed",
    "doesn't work",
    "did not work",
    "already tried",
    "i tried",
    "tried but",
    "same issue",
    "what next",
    "next step",
    "again",
    "still",
    "no change",
    "not solved",
    "not resolved",
]


class RAGMemoryHelper:
    """
    Lightweight RAG memory helper.
    Kept inside views.py so you don't need to create extra files now.
    """

    def clean_text(self, value):
        if not value:
            return ""

        value = str(value).strip()
        value = re.sub(r"\s+", " ", value)
        return value

    def normalize_history(self, chat_history):
        if not isinstance(chat_history, list):
            return []

        normalized = []

        for item in chat_history[-10:]:
            if not isinstance(item, dict):
                continue

            role = self.clean_text(item.get("role", "")).lower()
            content = self.clean_text(item.get("content", ""))

            if role not in ["user", "assistant"]:
                continue

            if not content:
                continue

            normalized.append(
                {
                    "role": role,
                    "content": content,
                }
            )

        return normalized

    def is_follow_up_question(self, question):
        question_lower = self.clean_text(question).lower()

        if len(question_lower.split()) <= 6:
            return True

        return any(keyword in question_lower for keyword in FOLLOW_UP_KEYWORDS)

    def build_history_text(self, chat_history):
        lines = []

        for item in chat_history[-8:]:
            role = "User" if item["role"] == "user" else "SmartDesk AI"
            lines.append(f"{role}: {item['content']}")

        return "\n".join(lines)

    def get_last_user_issue(self, chat_history):
        for item in reversed(chat_history):
            if item["role"] == "user":
                return item["content"]

        return ""

    def get_last_assistant_answer(self, chat_history):
        for item in reversed(chat_history):
            if item["role"] == "assistant":
                return item["content"]

        return ""

    def build_contextual_question(self, question, chat_history):
        question = self.clean_text(question)
        normalized_history = self.normalize_history(chat_history)

        if not normalized_history:
            return question

        if not self.is_follow_up_question(question):
            return question

        history_text = self.build_history_text(normalized_history)
        last_user_issue = self.get_last_user_issue(normalized_history)
        last_assistant_answer = self.get_last_assistant_answer(normalized_history)

        return f"""
The user is continuing the same SmartDesk support conversation.

Previous conversation:
{history_text}

Previous / original issue:
{last_user_issue}

Previous SmartDesk AI suggestion already given:
{last_assistant_answer}

Current user follow-up:
{question}

The user says the previous solution did not solve the issue.
Give next-level troubleshooting steps.
Do not repeat the exact same basic steps unless they are required for confirmation.
Mention what to check next and when to create a support ticket.
""".strip()

    def build_ticket_description_from_conversation(
        self,
        question,
        rag_answer,
        conversation,
    ):
        lines = [
            "Issue raised from SmartDesk RAG chat.",
            "",
            "Latest user question:",
            question or "No question provided.",
            "",
            "Latest SmartDesk AI answer:",
            rag_answer or "No AI answer available.",
        ]

        normalized_conversation = self.normalize_history(conversation)

        if normalized_conversation:
            lines.extend(
                [
                    "",
                    "Full RAG conversation:",
                    "----------------------",
                ]
            )

            for item in normalized_conversation:
                role = "USER" if item["role"] == "user" else "SMARTDESK AI"
                lines.append(f"{role}: {item['content']}")

        return "\n".join(lines)


class KBDocumentUploadAPIView(generics.CreateAPIView):
    serializer_class = KBDocumentUploadSerializer
    permission_classes = [IsAdminRole]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        document = serializer.save(
            uploaded_by=request.user,
            status=KBDocument.Status.PROCESSING,
        )

        processed_document = process_kb_document(document)

        response_status = (
            status.HTTP_201_CREATED
            if processed_document.status == KBDocument.Status.COMPLETED
            else status.HTTP_400_BAD_REQUEST
        )

        return Response(
            {
                "status": (
                    "success"
                    if processed_document.status == KBDocument.Status.COMPLETED
                    else "error"
                ),
                "message": (
                    "Knowledge base document uploaded and processed successfully."
                    if processed_document.status == KBDocument.Status.COMPLETED
                    else "Document uploaded but processing failed."
                ),
                "document": KBDocumentSerializer(
                    processed_document,
                    context={"request": request},
                ).data,
            },
            status=response_status,
        )


class KBDocumentListAPIView(generics.ListAPIView):
    serializer_class = KBDocumentSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return KBDocument.objects.all().order_by("-created_at")


class KBDocumentDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = KBDocumentSerializer
    permission_classes = [IsAdminRole]
    lookup_url_kwarg = "document_id"

    def get_queryset(self):
        return KBDocument.objects.all()

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()

        try:
            vector_store = VectorStoreService()
            vector_store.delete_document_chunks(document.id)
        except Exception:
            pass

        document.delete()

        return Response(
            {
                "status": "success",
                "message": "Knowledge base document deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


class RAGAskAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RAGAskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"]

        # Read these from request.data directly so this works even if your serializer
        # has not yet added session_id/chat_history fields.
        session_id = request.data.get("session_id", "")
        chat_history = request.data.get("chat_history", [])

        memory_helper = RAGMemoryHelper()
        contextual_question = memory_helper.build_contextual_question(
            question=question,
            chat_history=chat_history,
        )

        result = ask_rag(contextual_question)

        if not isinstance(result, dict):
            result = {
                "answer": str(result),
                "sources": [],
            }

        result["session_id"] = session_id
        result["original_question"] = question
        result["contextual_question"] = contextual_question

        if not result.get("suggested_ticket_subject"):
            result["suggested_ticket_subject"] = question[:120]

        if not result.get("suggested_ticket_description"):
            result["suggested_ticket_description"] = (
                f"User asked: {question}\n\n"
                f"SmartDesk AI answer: {result.get('answer', '')}"
            )

        return Response(
            {
                "status": "success",
                "result": result,
            },
            status=status.HTTP_200_OK,
        )


class CreateTicketFromRAGAPIView(APIView):
    permission_classes = [IsUserRole]

    def post(self, request):
        serializer = CreateTicketFromRAGSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"]
        rag_answer = serializer.validated_data.get("rag_answer", "")

        subject = serializer.validated_data.get("subject", "").strip()
        description = serializer.validated_data.get("description", "").strip()

        # Read conversation directly so this works without changing serializer now.
        conversation = request.data.get("conversation", [])

        if not subject:
            subject = question[:120]

        if conversation:
            memory_helper = RAGMemoryHelper()
            description = memory_helper.build_ticket_description_from_conversation(
                question=question,
                rag_answer=rag_answer,
                conversation=conversation,
            )

        if not description:
            description = (
                f"User question from knowledge base search:\n{question}\n\n"
                f"AI answer shown to user:\n{rag_answer or 'No answer generated.'}\n\n"
                "User still needs support from an agent."
            )

        ticket = Ticket.objects.create(
            user=request.user,
            subject=subject,
            description=description,
        )

        TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            sender_role=TicketMessage.SenderRole.USER,
            message=description,
        )

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="TICKET_CREATED_FROM_RAG",
            new_value=Ticket.Status.OPEN,
            note="Ticket created from RAG answer flow.",
        )

        from apps.ai_engine.ticket_classifier import classify_ticket
        from apps.tickets.models import TicketAIClassification

        classification = classify_ticket(
            subject=ticket.subject,
            description=ticket.description,
        )

        ticket.request_type = classification["request_type"]
        ticket.priority = classification["priority"]
        ticket.sentiment = classification["sentiment"]
        ticket.ai_summary = classification["summary"]
        ticket.ai_suggested_solution = classification["suggested_solution"]
        ticket.escalation_required = classification["escalation_required"]
        ticket.save(
            update_fields=[
                "request_type",
                "priority",
                "sentiment",
                "ai_summary",
                "ai_suggested_solution",
                "escalation_required",
                "updated_at",
            ]
        )

        TicketAIClassification.objects.create(
            ticket=ticket,
            request_type=classification["request_type"],
            priority=classification["priority"],
            sentiment=classification["sentiment"],
            confidence_score=classification["confidence_score"],
            reason=classification["reason"],
            model_used=classification["model_used"],
        )

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="AI_CLASSIFIED",
            new_value=(
                f'{classification["request_type"]} | '
                f'{classification["priority"]} | '
                f'{classification["sentiment"]}'
            ),
            note=classification["reason"],
        )

        return Response(
            {
                "status": "success",
                "message": "Ticket created from RAG answer successfully.",
                "ticket": {
                    "id": ticket.id,
                    "subject": ticket.subject,
                    "description": ticket.description,
                    "request_type": ticket.request_type,
                    "priority": ticket.priority,
                    "status": ticket.status,
                    "sentiment": ticket.sentiment,
                    "status_color": ticket.status_color,
                    "status_badge_class": ticket.status_badge_class,
                    "priority_badge_class": ticket.priority_badge_class,
                    "created_at": ticket.created_at,
                },
            },
            status=status.HTTP_201_CREATED,
        )