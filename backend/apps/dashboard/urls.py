from django.urls import path

from .views import AgentDashboardStatsAPIView


urlpatterns = [
    path("dashboard/", AgentDashboardStatsAPIView.as_view(), name="agent-dashboard"),
]