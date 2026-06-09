from django.urls import path

from .agent_views import (
    AgentQueueListAPIView,
    AgentTicketAISuggestAPIView,
    AgentTicketCloseAPIView,
    AgentTicketDetailAPIView,
    AgentTicketEscalateAPIView,
    AgentTicketReplyAPIView,
)


urlpatterns = [
    path("queue/", AgentQueueListAPIView.as_view(), name="agent-queue"),
    path("tickets/<int:ticket_id>/", AgentTicketDetailAPIView.as_view(), name="agent-ticket-detail"),
    path("tickets/<int:ticket_id>/reply/", AgentTicketReplyAPIView.as_view(), name="agent-ticket-reply"),
    path("tickets/<int:ticket_id>/close/", AgentTicketCloseAPIView.as_view(), name="agent-ticket-close"),
    path("tickets/<int:ticket_id>/escalate/", AgentTicketEscalateAPIView.as_view(), name="agent-ticket-escalate"),
    path("tickets/<int:ticket_id>/ai-suggest/", AgentTicketAISuggestAPIView.as_view(), name="agent-ticket-ai-suggest"),
]