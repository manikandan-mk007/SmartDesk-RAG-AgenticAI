import os

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Ticket,
    TicketActivityLog,
    TicketAttachment,
    TicketFeedback,
    TicketMessage,
)
from .serializers import (
    TicketAttachmentCreateSerializer,
    TicketAttachmentSerializer,
    TicketCreateSerializer,
    TicketDetailSerializer,
    TicketFeedbackSerializer,
    TicketListSerializer,
    TicketMessageCreateSerializer,
    TicketMessageSerializer,
)


User = get_user_model()


def get_file_type(filename):
    ext = os.path.splitext(filename)[1].lower()

    image_exts = [".jpg", ".jpeg", ".png", ".webp"]
    video_exts = [".mp4", ".mov", ".avi"]
    document_exts = [".pdf", ".doc", ".docx", ".txt"]

    if ext in image_exts:
        return TicketAttachment.FileType.IMAGE

    if ext in video_exts:
        return TicketAttachment.FileType.VIDEO

    if ext in document_exts:
        return TicketAttachment.FileType.DOCUMENT

    return TicketAttachment.FileType.OTHER


def analyze_attachment_if_supported(attachment):
    try:
        if attachment.file_type == TicketAttachment.FileType.IMAGE:
            from apps.ai_engine.image_analyzer import analyze_image_attachment

            result = analyze_image_attachment(attachment.file.path)
            attachment.analysis_result = result.get(
                "summary",
                "Image analysis completed.",
            )
            attachment.save(update_fields=["analysis_result"])

            return attachment.analysis_result

        if attachment.file_type == TicketAttachment.FileType.VIDEO:
            from apps.ai_engine.video_analyzer import analyze_video_attachment

            result = analyze_video_attachment(attachment.file.path)
            attachment.analysis_result = result.get(
                "summary",
                "Video analysis completed.",
            )
            attachment.save(update_fields=["analysis_result"])

            return attachment.analysis_result

        attachment.analysis_result = (
            "This attachment type does not support automatic image/video analysis."
        )
        attachment.save(update_fields=["analysis_result"])

        return attachment.analysis_result

    except Exception as exc:
        attachment.analysis_result = (
            f"Automatic attachment analysis failed. Reason: {str(exc)}"
        )
        attachment.save(update_fields=["analysis_result"])
        return attachment.analysis_result


def normalize_department(value):
    value = str(value or "").strip().upper()

    if value in ["IT", "INFORMATION TECHNOLOGY", "TECH", "TECHNICAL"]:
        return Ticket.RequestType.IT

    if value in ["HR", "HUMAN RESOURCE", "HUMAN RESOURCES"]:
        return Ticket.RequestType.HR

    if value in ["FACILITY", "FACILITIES", "FACILITY MANAGEMENT"]:
        return Ticket.RequestType.FACILITIES

    return value


def get_agent_department(user):
    try:
        employee_record = user.employee_record
    except Exception:
        return ""

    return normalize_department(employee_record.department)


def is_agent_department_allowed(user, ticket):
    agent_department = get_agent_department(user)

    if not agent_department:
        return False

    return ticket.request_type == agent_department


def can_user_access_ticket(user, ticket):
    if not user or not user.is_authenticated:
        return False

    if user.role == "ADMIN":
        return True

    if user.role == "USER":
        return ticket.user_id == user.id

    if user.role == "AGENT":
        if not is_agent_department_allowed(user, ticket):
            return False

        if ticket.assigned_agent_id is None:
            return True

        return ticket.assigned_agent_id == user.id

    return False


def claim_ticket_for_agent(user, ticket_id):
    with transaction.atomic():
        try:
            ticket = Ticket.objects.select_for_update().get(id=ticket_id)
        except Ticket.DoesNotExist:
            return None, Response(
                {
                    "status": "error",
                    "message": "Ticket not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.role != "AGENT":
            return ticket, None

        if not is_agent_department_allowed(user, ticket):
            return None, Response(
                {
                    "status": "error",
                    "message": (
                        "You cannot access this ticket because it does not belong "
                        "to your department."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if ticket.assigned_agent_id and ticket.assigned_agent_id != user.id:
            return None, Response(
                {
                    "status": "error",
                    "message": (
                        "This ticket is already being handled by "
                        f"{ticket.assigned_agent.full_name}."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if ticket.assigned_agent_id is None:
            old_status = ticket.status

            ticket.assigned_agent = user

            if ticket.status == Ticket.Status.OPEN:
                ticket.status = Ticket.Status.IN_PROGRESS

            ticket.save(
                update_fields=[
                    "assigned_agent",
                    "status",
                    "updated_at",
                ]
            )

            TicketActivityLog.objects.create(
                ticket=ticket,
                performed_by=user,
                action="TICKET_ASSIGNED",
                old_value="Not assigned",
                new_value=user.full_name,
                note="Ticket automatically assigned when agent opened it.",
            )

            if old_status != ticket.status:
                TicketActivityLog.objects.create(
                    ticket=ticket,
                    performed_by=user,
                    action="STATUS_CHANGED",
                    old_value=old_status,
                    new_value=ticket.status,
                    note="Ticket moved to in progress after agent claimed it.",
                )

        return ticket, None


def ensure_agent_owns_ticket(user, ticket):
    if user.role != "AGENT":
        return True, None

    if ticket.assigned_agent_id != user.id:
        return False, Response(
            {
                "status": "error",
                "message": "You cannot update this ticket because another agent is handling it.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    return True, None


class TicketCreateAPIView(generics.CreateAPIView):
    serializer_class = TicketCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.role != "USER":
            return Response(
                {
                    "status": "error",
                    "message": "Only normal users can create tickets.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()

        return Response(
            {
                "status": "success",
                "message": "Ticket created successfully.",
                "ticket": TicketDetailSerializer(
                    ticket,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class MyTicketListAPIView(generics.ListAPIView):
    serializer_class = TicketListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).order_by("-created_at")


class TicketDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        if request.user.role == "AGENT":
            ticket, error_response = claim_ticket_for_agent(request.user, ticket_id)

            if error_response:
                return error_response
        else:
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

        if not can_user_access_ticket(request.user, ticket):
            return Response(
                {
                    "status": "error",
                    "message": "You do not have permission to view this ticket.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {
                "status": "success",
                "message": "Ticket details fetched successfully.",
                "ticket": TicketDetailSerializer(
                    ticket,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class TicketMessageCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):
        if request.user.role == "AGENT":
            ticket, error_response = claim_ticket_for_agent(request.user, ticket_id)

            if error_response:
                return error_response
        else:
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

        if not can_user_access_ticket(request.user, ticket):
            return Response(
                {
                    "status": "error",
                    "message": "You do not have permission to reply to this ticket.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        owns_ticket, error_response = ensure_agent_owns_ticket(request.user, ticket)

        if error_response:
            return error_response

        if ticket.status == Ticket.Status.CLOSED:
            return Response(
                {
                    "status": "error",
                    "message": "Cannot send message because this ticket is already closed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TicketMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            sender_role=request.user.role,
            message=serializer.validated_data["message"],
        )

        old_status = ticket.status

        if request.user.role == "AGENT" and ticket.status == Ticket.Status.OPEN:
            ticket.status = Ticket.Status.IN_PROGRESS
            ticket.save(update_fields=["status", "updated_at"])

            TicketActivityLog.objects.create(
                ticket=ticket,
                performed_by=request.user,
                action="STATUS_CHANGED",
                old_value=old_status,
                new_value=Ticket.Status.IN_PROGRESS,
                note="Ticket moved to in progress after agent reply.",
            )

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="MESSAGE_ADDED",
            note="New message added to ticket thread.",
        )

        return Response(
            {
                "status": "success",
                "message": "Message sent successfully.",
                "ticket_message": TicketMessageSerializer(message).data,
            },
            status=status.HTTP_201_CREATED,
        )


class TicketAttachmentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, ticket_id):
        if request.user.role == "AGENT":
            ticket, error_response = claim_ticket_for_agent(request.user, ticket_id)

            if error_response:
                return error_response
        else:
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

        if not can_user_access_ticket(request.user, ticket):
            return Response(
                {
                    "status": "error",
                    "message": "You do not have permission to upload attachment for this ticket.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        owns_ticket, error_response = ensure_agent_owns_ticket(request.user, ticket)

        if error_response:
            return error_response

        serializer = TicketAttachmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["file"]

        attachment = TicketAttachment.objects.create(
            ticket=ticket,
            uploaded_by=request.user,
            file=uploaded_file,
            file_type=get_file_type(uploaded_file.name),
            original_filename=uploaded_file.name,
        )

        analysis_result = analyze_attachment_if_supported(attachment)

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="ATTACHMENT_ADDED",
            new_value=attachment.file_type,
            note=f"Attachment uploaded: {uploaded_file.name}",
        )

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="ATTACHMENT_ANALYZED",
            new_value=attachment.file_type,
            note=analysis_result[:500],
        )

        return Response(
            {
                "status": "success",
                "message": "Attachment uploaded and analyzed successfully.",
                "attachment": TicketAttachmentSerializer(
                    attachment,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class TicketFeedbackCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

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

        if ticket.user_id != request.user.id:
            return Response(
                {
                    "status": "error",
                    "message": "Only the ticket owner can submit feedback.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if ticket.status != Ticket.Status.CLOSED:
            return Response(
                {
                    "status": "error",
                    "message": "Feedback can be submitted only after ticket is closed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if TicketFeedback.objects.filter(ticket=ticket).exists():
            return Response(
                {
                    "status": "error",
                    "message": "Feedback already submitted for this ticket.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TicketFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        feedback = serializer.save(
            ticket=ticket,
            user=request.user,
            agent=ticket.assigned_agent,
        )

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="FEEDBACK_SUBMITTED",
            new_value=str(feedback.rating),
            note="User submitted feedback.",
        )

        return Response(
            {
                "status": "success",
                "message": "Feedback submitted successfully.",
                "feedback": TicketFeedbackSerializer(feedback).data,
            },
            status=status.HTTP_201_CREATED,
        )


class TicketStatusOptionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = [
            {
                "value": Ticket.Status.OPEN,
                "label": "Open",
                "color": "red",
                "badge_class": "bg-red-100 text-red-700 border-red-200",
            },
            {
                "value": Ticket.Status.IN_PROGRESS,
                "label": "In Progress",
                "color": "yellow",
                "badge_class": "bg-yellow-100 text-yellow-700 border-yellow-200",
            },
            {
                "value": Ticket.Status.CLOSED,
                "label": "Closed",
                "color": "green",
                "badge_class": "bg-green-100 text-green-700 border-green-200",
            },
            {
                "value": Ticket.Status.ESCALATED,
                "label": "Escalated",
                "color": "purple",
                "badge_class": "bg-purple-100 text-purple-700 border-purple-200",
            },
        ]

        return Response(
            {
                "status": "success",
                "message": "Ticket status options fetched successfully.",
                "statuses": data,
            },
            status=status.HTTP_200_OK,
        )


class AgentTicketQueueAPIView(generics.ListAPIView):
    serializer_class = TicketListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role not in ["AGENT", "ADMIN"]:
            return Ticket.objects.none()

        if user.role == "ADMIN":
            return Ticket.objects.all().order_by("-created_at")

        agent_department = get_agent_department(user)

        if not agent_department:
            return Ticket.objects.none()

        return (
            Ticket.objects.filter(request_type=agent_department)
            .filter(Q(assigned_agent__isnull=True) | Q(assigned_agent=user))
            .order_by("-created_at")
        )


class AgentFeedbackSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "AGENT":
            return Response(
                {
                    "status": "error",
                    "message": "Only agents can view feedback summary.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = TicketFeedback.objects.filter(agent=request.user)

        total_feedback = queryset.count()
        average_rating = queryset.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0
        five_star_count = queryset.filter(rating=5).count()
        low_rating_count = queryset.filter(rating__lte=2).count()

        latest_feedback = TicketFeedbackSerializer(
            queryset.select_related("ticket", "user", "agent")[:5],
            many=True,
        ).data

        return Response(
            {
                "status": "success",
                "message": "Agent feedback summary fetched successfully.",
                "summary": {
                    "average_rating": round(float(average_rating), 2),
                    "total_feedback": total_feedback,
                    "five_star_count": five_star_count,
                    "low_rating_count": low_rating_count,
                    "latest_feedback": latest_feedback,
                },
            },
            status=status.HTTP_200_OK,
        )


class AgentFeedbackListAPIView(generics.ListAPIView):
    serializer_class = TicketFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role != "AGENT":
            return TicketFeedback.objects.none()

        return (
            TicketFeedback.objects.filter(agent=user)
            .select_related("ticket", "user", "agent")
            .order_by("-created_at")
        )


class AdminAgentFeedbackAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "status": "error",
                    "message": "Only admins can view agent feedback analytics.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        agents = (
            User.objects.filter(role="AGENT")
            .annotate(
                closed_tickets=Count(
                    "assigned_tickets",
                    filter=Q(assigned_tickets__status=Ticket.Status.CLOSED),
                    distinct=True,
                ),
                feedback_count=Count(
                    "received_ticket_feedbacks",
                    distinct=True,
                ),
                average_rating=Avg("received_ticket_feedbacks__rating"),
                low_rating_count=Count(
                    "received_ticket_feedbacks",
                    filter=Q(received_ticket_feedbacks__rating__lte=2),
                    distinct=True,
                ),
            )
            .order_by("full_name")
        )

        analytics = []

        for agent in agents:
            analytics.append(
                {
                    "agent_id": agent.id,
                    "agent_name": agent.full_name,
                    "agent_email": agent.email,
                    "agent_department": get_agent_department(agent) or "-",
                    "closed_tickets": agent.closed_tickets,
                    "feedback_count": agent.feedback_count,
                    "average_rating": round(float(agent.average_rating or 0), 2),
                    "low_rating_count": agent.low_rating_count,
                }
            )

        return Response(
            {
                "status": "success",
                "message": "Agent feedback analytics fetched successfully.",
                "analytics": analytics,
            },
            status=status.HTTP_200_OK,
        )