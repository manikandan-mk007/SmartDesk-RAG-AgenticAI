from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAgentOrAdminRole
from apps.tickets.models import Ticket


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


def build_workload_insight(
    total_open: int,
    high_priority: int,
    today_queue: int,
    request_type_counts: list[dict],
) -> str:
    if total_open == 0:
        return "No open tickets are currently waiting in the queue."

    top_request_type = None

    if request_type_counts:
        top_request_type = max(
            request_type_counts,
            key=lambda item: item["count"],
        )

    insight_parts = []

    insight_parts.append(
        f"There are {total_open} open tickets and {today_queue} tickets in today's queue."
    )

    if high_priority > 0:
        insight_parts.append(
            f"{high_priority} high priority tickets need quick attention."
        )

    if top_request_type:
        insight_parts.append(
            f"Most tickets are currently related to {top_request_type['label']}."
        )

    if high_priority >= 5:
        insight_parts.append(
            "Recommended action: assign more agents to high priority tickets first."
        )
    elif today_queue >= 10:
        insight_parts.append(
            "Recommended action: clear today's queue before handling low priority requests."
        )
    else:
        insight_parts.append(
            "Recommended action: continue resolving open tickets based on priority and created time."
        )

    return " ".join(insight_parts)


class AgentDashboardStatsAPIView(APIView):
    permission_classes = [IsAgentOrAdminRole]

    def get(self, request):
        today = timezone.localdate()

        all_tickets = Ticket.objects.all()

        total_tickets = all_tickets.count()
        open_tickets = all_tickets.filter(status=Ticket.Status.OPEN).count()
        in_progress_tickets = all_tickets.filter(status=Ticket.Status.IN_PROGRESS).count()
        closed_tickets = all_tickets.filter(status=Ticket.Status.CLOSED).count()
        escalated_tickets = all_tickets.filter(status=Ticket.Status.ESCALATED).count()

        high_priority_tickets = all_tickets.filter(priority=Ticket.Priority.HIGH).count()

        today_queue_count = all_tickets.filter(
            created_at__date=today,
        ).exclude(
            status=Ticket.Status.CLOSED,
        ).count()

        assigned_to_me_count = 0

        if request.user.role == "AGENT":
            assigned_to_me_count = all_tickets.filter(
                assigned_agent=request.user,
            ).exclude(
                status=Ticket.Status.CLOSED,
            ).count()

        request_type_counts = count_by_field(all_tickets, "request_type")
        priority_counts = count_by_field(all_tickets, "priority")
        sentiment_counts = count_by_field(all_tickets, "sentiment")
        status_counts = count_by_field(all_tickets, "status")

        recent_tickets = all_tickets.order_by("-created_at")[:5]

        recent_ticket_data = [
            {
                "id": ticket.id,
                "subject": ticket.subject,
                "request_type": ticket.request_type,
                "priority": ticket.priority,
                "status": ticket.status,
                "sentiment": ticket.sentiment,
                "status_color": ticket.status_color,
                "status_badge_class": ticket.status_badge_class,
                "priority_badge_class": ticket.priority_badge_class,
                "created_at": ticket.created_at,
            }
            for ticket in recent_tickets
        ]

        ai_workload_insight = build_workload_insight(
            total_open=open_tickets,
            high_priority=high_priority_tickets,
            today_queue=today_queue_count,
            request_type_counts=request_type_counts,
        )

        return Response(
            {
                "status": "success",
                "message": "Agent dashboard statistics fetched successfully.",
                "dashboard": {
                    "cards": {
                        "total_tickets": total_tickets,
                        "open_tickets": open_tickets,
                        "in_progress_tickets": in_progress_tickets,
                        "closed_tickets": closed_tickets,
                        "escalated_tickets": escalated_tickets,
                        "high_priority_tickets": high_priority_tickets,
                        "today_queue_count": today_queue_count,
                        "assigned_to_me_count": assigned_to_me_count,
                    },
                    "charts": {
                        "tickets_by_request_type": request_type_counts,
                        "tickets_by_priority": priority_counts,
                        "tickets_by_sentiment": sentiment_counts,
                        "tickets_by_status": status_counts,
                    },
                    "recent_tickets": recent_ticket_data,
                    "ai_workload_insight": ai_workload_insight,
                },
            },
            status=status.HTTP_200_OK,
        )