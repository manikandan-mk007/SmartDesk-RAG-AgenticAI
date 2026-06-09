from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAgentOrAdminRole

from .models import Ticket, TicketActivityLog, TicketAgentSuggestion, TicketMessage
from .serializers import (
    AgentCloseTicketSerializer,
    AgentEscalateTicketSerializer,
    AgentReplySerializer,
    TicketAgentSuggestionSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
    TicketMessageSerializer,
)

class AgentQueueListAPIView(generics.ListAPIView):
    serializer_class = TicketListSerializer
    permission_classes = [IsAgentOrAdminRole]

    def get_queryset(self):
        queryset = Ticket.objects.all().order_by("-created_at")

        request_type = self.request.query_params.get("request_type", "").strip().upper()
        priority = self.request.query_params.get("priority", "").strip().upper()
        ticket_status = self.request.query_params.get("status", "").strip().upper()
        sentiment = self.request.query_params.get("sentiment", "").strip().upper()
        search_query = self.request.query_params.get("q", "").strip()

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


class AgentTicketDetailAPIView(APIView):
    permission_classes = [IsAgentOrAdminRole]

    def get(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Ticket not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "status": "success",
                "message": "Agent ticket details fetched successfully.",
                "ticket": TicketDetailSerializer(
                    ticket,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class AgentTicketReplyAPIView(APIView):
    permission_classes = [IsAgentOrAdminRole]

    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Ticket not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if ticket.status == Ticket.Status.CLOSED:
            return Response(
                {
                    "status": "error",
                    "message": "Cannot reply because this ticket is already closed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AgentReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = ticket.status
        old_agent = ticket.assigned_agent

        if ticket.assigned_agent is None and request.user.role == "AGENT":
            ticket.assigned_agent = request.user

        if ticket.status == Ticket.Status.OPEN:
            ticket.status = Ticket.Status.IN_PROGRESS

        ticket.save(
            update_fields=[
                "assigned_agent",
                "status",
                "updated_at",
            ]
        )

        message = TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            sender_role=request.user.role,
            message=serializer.validated_data["message"],
        )

        if old_agent is None and ticket.assigned_agent is not None:
            TicketActivityLog.objects.create(
                ticket=ticket,
                performed_by=request.user,
                action="AGENT_ASSIGNED",
                old_value="",
                new_value=ticket.assigned_agent.email,
                note="Ticket assigned automatically when agent replied.",
            )

        if old_status != ticket.status:
            TicketActivityLog.objects.create(
                ticket=ticket,
                performed_by=request.user,
                action="STATUS_CHANGED",
                old_value=old_status,
                new_value=ticket.status,
                note="Ticket moved to in progress after agent reply.",
            )

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="AGENT_REPLIED",
            note="Agent added a reply to the ticket thread.",
        )

        return Response(
            {
                "status": "success",
                "message": "Agent reply sent successfully.",
                "ticket_message": TicketMessageSerializer(message).data,
                "ticket": TicketDetailSerializer(
                    ticket,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AgentTicketCloseAPIView(APIView):
    permission_classes = [IsAgentOrAdminRole]

    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Ticket not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if ticket.status == Ticket.Status.CLOSED:
            return Response(
                {
                    "status": "error",
                    "message": "Ticket is already closed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AgentCloseTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        closing_note = serializer.validated_data.get("closing_note", "").strip()

        old_status = ticket.status
        ticket.status = Ticket.Status.CLOSED
        ticket.closed_at = timezone.now()

        if ticket.assigned_agent is None and request.user.role == "AGENT":
            ticket.assigned_agent = request.user

        ticket.save(
            update_fields=[
                "status",
                "closed_at",
                "assigned_agent",
                "updated_at",
            ]
        )

        if closing_note:
            TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                sender_role=request.user.role,
                message=closing_note,
            )

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="TICKET_CLOSED",
            old_value=old_status,
            new_value=Ticket.Status.CLOSED,
            note=closing_note or "Ticket closed by agent.",
        )

        return Response(
            {
                "status": "success",
                "message": "Ticket closed successfully.",
                "ticket": TicketDetailSerializer(
                    ticket,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class AgentTicketEscalateAPIView(APIView):
    permission_classes = [IsAgentOrAdminRole]

    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Ticket not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if ticket.status == Ticket.Status.CLOSED:
            return Response(
                {
                    "status": "error",
                    "message": "Cannot escalate a closed ticket.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AgentEscalateTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reason = serializer.validated_data.get("reason", "").strip()

        old_status = ticket.status
        old_priority = ticket.priority

        ticket.status = Ticket.Status.ESCALATED
        ticket.priority = Ticket.Priority.HIGH
        ticket.escalation_required = True

        if ticket.assigned_agent is None and request.user.role == "AGENT":
            ticket.assigned_agent = request.user

        ticket.save(
            update_fields=[
                "status",
                "priority",
                "escalation_required",
                "assigned_agent",
                "updated_at",
            ]
        )

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="TICKET_ESCALATED",
            old_value=f"{old_status} | {old_priority}",
            new_value=f"{Ticket.Status.ESCALATED} | {Ticket.Priority.HIGH}",
            note=reason or "Ticket escalated by agent.",
        )

        if reason:
            TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                sender_role=request.user.role,
                message=f"Escalation note: {reason}",
            )

        return Response(
            {
                "status": "success",
                "message": "Ticket escalated successfully.",
                "ticket": TicketDetailSerializer(
                    ticket,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_200_OK,
        )
    
class AgentTicketAISuggestAPIView(APIView):
    permission_classes = [IsAgentOrAdminRole]

    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Ticket not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        from apps.ai_engine.agent_assist import generate_agent_assist

        suggestion_data = generate_agent_assist(ticket)

        suggestion = TicketAgentSuggestion.objects.create(
            ticket=ticket,
            generated_for=request.user,
            ticket_summary=suggestion_data["ticket_summary"],
            priority_reason=suggestion_data["priority_reason"],
            sentiment_explanation=suggestion_data["sentiment_explanation"],
            suggested_reply=suggestion_data["suggested_reply"],
            suggested_steps=suggestion_data["suggested_steps"],
            escalation_suggestion=suggestion_data["escalation_suggestion"],
            related_kb_articles=suggestion_data["related_kb_articles"],
            similar_tickets=suggestion_data["similar_tickets"],
            model_used=suggestion_data["model_used"],
            confidence_score=suggestion_data["confidence_score"],
        )

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="AI_AGENT_ASSIST_GENERATED",
            new_value=suggestion.model_used,
            note=suggestion.suggested_reply[:500],
        )

        return Response(
            {
                "status": "success",
                "message": "AI agent assist suggestion generated successfully.",
                "suggestion": TicketAgentSuggestionSerializer(suggestion).data,
            },
            status=status.HTTP_201_CREATED,
        )