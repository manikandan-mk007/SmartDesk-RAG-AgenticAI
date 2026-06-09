from django.urls import path

from .views import (
    AdminAgentFeedbackAnalyticsAPIView,
    AgentFeedbackListAPIView,
    AgentFeedbackSummaryAPIView,
    AgentTicketQueueAPIView,
    MyTicketListAPIView,
    TicketAttachmentCreateAPIView,
    TicketCreateAPIView,
    TicketDetailAPIView,
    TicketFeedbackCreateAPIView,
    TicketMessageCreateAPIView,
    TicketStatusOptionsAPIView,
)


urlpatterns = [
    path("", TicketCreateAPIView.as_view(), name="ticket-create"),
    path("my/", MyTicketListAPIView.as_view(), name="my-ticket-list"),
    path("status-options/", TicketStatusOptionsAPIView.as_view(), name="ticket-status-options"),

    # Agent ticket ownership + department queue
    path("agent/queue/", AgentTicketQueueAPIView.as_view(), name="agent-ticket-queue"),
    path("agent/feedback/summary/", AgentFeedbackSummaryAPIView.as_view(), name="agent-feedback-summary"),
    path("agent/feedback/", AgentFeedbackListAPIView.as_view(), name="agent-feedback-list"),

    # Admin feedback analytics
    path("admin/feedback/agent-analytics/", AdminAgentFeedbackAnalyticsAPIView.as_view(), name="admin-agent-feedback-analytics"),

    path("<int:ticket_id>/", TicketDetailAPIView.as_view(), name="ticket-detail"),
    path("<int:ticket_id>/messages/", TicketMessageCreateAPIView.as_view(), name="ticket-message-create"),
    path("<int:ticket_id>/attachments/", TicketAttachmentCreateAPIView.as_view(), name="ticket-attachment-create"),
    path("<int:ticket_id>/feedback/", TicketFeedbackCreateAPIView.as_view(), name="ticket-feedback-create"),
]