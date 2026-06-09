from collections import Counter

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole
from apps.faqs.models import FAQ
from apps.knowledge_base.models import KBDocument, KBChunk
from apps.tickets.models import (
    Ticket,
    TicketAIClassification,
    TicketAgentSuggestion,
    TicketFeedback,
)
from apps.tickets.serializers import (
    TicketAIClassificationSerializer,
    TicketListSerializer,
)


User = get_user_model()


def count_by_field(queryset, field_name: str) -> list[dict]:
    rows = (
        queryset.values(field_name)
        .annotate(count=Count("id"))
        .order_by(field_name)
    )

    return [
        {
            "label": row[field_name] or "UNKNOWN",
            "count": row["count"],
        }
        for row in rows
    ]


def get_ticket_queryset_from_params(request):
    queryset = Ticket.objects.all().order_by("-created_at")

    request_type = request.query_params.get("request_type", "").strip().upper()
    priority = request.query_params.get("priority", "").strip().upper()
    ticket_status = request.query_params.get("status", "").strip().upper()
    sentiment = request.query_params.get("sentiment", "").strip().upper()
    search_query = request.query_params.get("q", "").strip()

    if request_type:
        queryset = queryset.filter(request_type=request_type)

    if priority:
        queryset = queryset.filter(priority=priority)

    if ticket_status:
        queryset = queryset.filter(status=ticket_status)

    if sentiment:
        queryset = queryset.filter(sentiment=sentiment)

    if search_query:
        queryset = queryset.filter(
            Q(subject__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(user__full_name__icontains=search_query)
            | Q(user__email__icontains=search_query)
            | Q(ai_summary__icontains=search_query)
        )

    return queryset


def build_admin_insight(cards: dict, top_request_type: str | None) -> str:
    open_count = cards.get("open_tickets", 0)
    high_count = cards.get("high_priority_tickets", 0)
    today_count = cards.get("today_tickets", 0)

    if open_count == 0:
        return "All support queues are clear. No open tickets are pending right now."

    parts = [
        f"There are {open_count} open tickets and {today_count} tickets created today."
    ]

    if high_count:
        parts.append(f"{high_count} high priority tickets need immediate attention.")

    if top_request_type:
        parts.append(f"The most common request type is currently {top_request_type}.")

    if high_count >= 5:
        parts.append("Recommended action: assign more agents to high-priority tickets.")
    elif open_count >= 20:
        parts.append("Recommended action: increase queue monitoring and reduce backlog.")
    else:
        parts.append("Recommended action: continue resolving tickets by priority and age.")

    return " ".join(parts)


class AdminDashboardStatsAPIView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        today = timezone.localdate()

        tickets = Ticket.objects.all()
        users = User.objects.all()

        request_type_counts = count_by_field(tickets, "request_type")
        priority_counts = count_by_field(tickets, "priority")
        sentiment_counts = count_by_field(tickets, "sentiment")
        status_counts = count_by_field(tickets, "status")

        top_request_type = None
        if request_type_counts:
            top_request_type = max(request_type_counts, key=lambda item: item["count"])["label"]

        feedback_average = TicketFeedback.objects.aggregate(
            average_rating=Avg("rating")
        )["average_rating"]

        cards = {
            "total_users": users.filter(role=User.Role.USER).count(),
            "total_agents": users.filter(role=User.Role.AGENT).count(),
            "active_users": users.filter(role=User.Role.USER, is_active=True).count(),
            "active_agents": users.filter(role=User.Role.AGENT, is_active=True).count(),
            "total_tickets": tickets.count(),
            "open_tickets": tickets.filter(status=Ticket.Status.OPEN).count(),
            "in_progress_tickets": tickets.filter(status=Ticket.Status.IN_PROGRESS).count(),
            "closed_tickets": tickets.filter(status=Ticket.Status.CLOSED).count(),
            "escalated_tickets": tickets.filter(status=Ticket.Status.ESCALATED).count(),
            "high_priority_tickets": tickets.filter(priority=Ticket.Priority.HIGH).count(),
            "today_tickets": tickets.filter(created_at__date=today).count(),
            "total_faqs": FAQ.objects.count(),
            "active_faqs": FAQ.objects.filter(is_active=True).count(),
            "kb_documents": KBDocument.objects.count(),
            "completed_kb_documents": KBDocument.objects.filter(
                status=KBDocument.Status.COMPLETED
            ).count(),
            "kb_chunks": KBChunk.objects.count(),
            "ai_classifications": TicketAIClassification.objects.count(),
            "agent_suggestions": TicketAgentSuggestion.objects.count(),
            "average_feedback_rating": round(feedback_average or 0, 2),
        }

        recent_tickets = tickets.order_by("-created_at")[:8]

        return Response(
            {
                "status": "success",
                "message": "Admin dashboard statistics fetched successfully.",
                "dashboard": {
                    "cards": cards,
                    "charts": {
                        "tickets_by_request_type": request_type_counts,
                        "tickets_by_priority": priority_counts,
                        "tickets_by_sentiment": sentiment_counts,
                        "tickets_by_status": status_counts,
                    },
                    "recent_tickets": TicketListSerializer(recent_tickets, many=True).data,
                    "admin_insight": build_admin_insight(cards, top_request_type),
                },
            },
            status=status.HTTP_200_OK,
        )


class AdminTicketListAPIView(generics.ListAPIView):
    serializer_class = TicketListSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return get_ticket_queryset_from_params(self.request)


class AdminTicketAnalyticsAPIView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        tickets = get_ticket_queryset_from_params(request)

        total = tickets.count()
        closed = tickets.filter(status=Ticket.Status.CLOSED).count()
        open_count = tickets.filter(status=Ticket.Status.OPEN).count()
        escalated = tickets.filter(status=Ticket.Status.ESCALATED).count()

        closure_rate = 0
        if total > 0:
            closure_rate = round((closed / total) * 100, 2)

        analytics = {
            "total_tickets": total,
            "open_tickets": open_count,
            "closed_tickets": closed,
            "escalated_tickets": escalated,
            "closure_rate_percent": closure_rate,
            "tickets_by_request_type": count_by_field(tickets, "request_type"),
            "tickets_by_priority": count_by_field(tickets, "priority"),
            "tickets_by_sentiment": count_by_field(tickets, "sentiment"),
            "tickets_by_status": count_by_field(tickets, "status"),
        }

        return Response(
            {
                "status": "success",
                "message": "Admin ticket analytics fetched successfully.",
                "analytics": analytics,
            },
            status=status.HTTP_200_OK,
        )


class AdminAIClassificationLogsAPIView(generics.ListAPIView):
    serializer_class = TicketAIClassificationSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        queryset = TicketAIClassification.objects.select_related("ticket").order_by("-created_at")

        request_type = self.request.query_params.get("request_type", "").strip().upper()
        priority = self.request.query_params.get("priority", "").strip().upper()
        sentiment = self.request.query_params.get("sentiment", "").strip().upper()
        model_used = self.request.query_params.get("model_used", "").strip()

        if request_type:
            queryset = queryset.filter(request_type=request_type)

        if priority:
            queryset = queryset.filter(priority=priority)

        if sentiment:
            queryset = queryset.filter(sentiment=sentiment)

        if model_used:
            queryset = queryset.filter(model_used__icontains=model_used)

        return queryset


class AdminKBGapsAPIView(APIView):
    permission_classes = [IsAdminRole]

    STOP_WORDS = {
        "this",
        "that",
        "with",
        "from",
        "have",
        "need",
        "please",
        "issue",
        "ticket",
        "problem",
        "system",
        "company",
        "after",
        "before",
        "today",
        "still",
        "getting",
        "showing",
        "working",
        "not",
        "and",
        "the",
        "for",
        "can",
        "you",
        "my",
        "is",
        "are",
        "was",
        "were",
    }

    def get_keywords_from_tickets(self):
        tickets = Ticket.objects.all().order_by("-created_at")[:200]

        words = []

        for ticket in tickets:
            text = f"{ticket.subject} {ticket.description} {ticket.ai_summary}".lower()

            for word in text.split():
                word = word.strip(".,!?;:()[]{}'\"").lower()

                if len(word) < 5:
                    continue

                if word in self.STOP_WORDS:
                    continue

                words.append(word)

        return Counter(words).most_common(20)

    def get(self, request):
        common_keywords = self.get_keywords_from_tickets()

        gaps = []

        for keyword, count in common_keywords:
            kb_exists = KBChunk.objects.filter(chunk_text__icontains=keyword).exists()

            if not kb_exists:
                matching_tickets = Ticket.objects.filter(
                    Q(subject__icontains=keyword)
                    | Q(description__icontains=keyword)
                    | Q(ai_summary__icontains=keyword)
                ).order_by("-created_at")[:5]

                gaps.append(
                    {
                        "missing_topic": keyword,
                        "ticket_count": count,
                        "recommendation": (
                            f"Create or improve KB content for '{keyword}' because it appears "
                            "in support tickets but is not clearly covered in the knowledge base."
                        ),
                        "sample_tickets": [
                            {
                                "id": ticket.id,
                                "subject": ticket.subject,
                                "request_type": ticket.request_type,
                                "priority": ticket.priority,
                                "status": ticket.status,
                            }
                            for ticket in matching_tickets
                        ],
                    }
                )

        return Response(
            {
                "status": "success",
                "message": "KB gap analysis completed successfully.",
                "gaps": gaps[:10],
            },
            status=status.HTTP_200_OK,
        )


class AdminReportSummaryAPIView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        tickets = get_ticket_queryset_from_params(request)

        feedback_average = TicketFeedback.objects.aggregate(
            average_rating=Avg("rating")
        )["average_rating"]

        report = {
            "report_name": "SmartDesk Admin Support Report",
            "generated_at": timezone.now(),
            "summary": {
                "total_tickets": tickets.count(),
                "open_tickets": tickets.filter(status=Ticket.Status.OPEN).count(),
                "in_progress_tickets": tickets.filter(status=Ticket.Status.IN_PROGRESS).count(),
                "closed_tickets": tickets.filter(status=Ticket.Status.CLOSED).count(),
                "escalated_tickets": tickets.filter(status=Ticket.Status.ESCALATED).count(),
                "high_priority_tickets": tickets.filter(priority=Ticket.Priority.HIGH).count(),
                "average_feedback_rating": round(feedback_average or 0, 2),
            },
            "breakdowns": {
                "request_type": count_by_field(tickets, "request_type"),
                "priority": count_by_field(tickets, "priority"),
                "sentiment": count_by_field(tickets, "sentiment"),
                "status": count_by_field(tickets, "status"),
            },
            "export_note": (
                "This JSON report can be used by the frontend to generate PDF, CSV, "
                "or dashboard report views."
            ),
        }

        return Response(
            {
                "status": "success",
                "message": "Admin report summary generated successfully.",
                "report": report,
            },
            status=status.HTTP_200_OK,
        )