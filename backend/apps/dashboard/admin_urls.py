from django.urls import path

from .admin_views import (
    AdminAIClassificationLogsAPIView,
    AdminDashboardStatsAPIView,
    AdminKBGapsAPIView,
    AdminReportSummaryAPIView,
    AdminTicketAnalyticsAPIView,
    AdminTicketListAPIView,
)


urlpatterns = [
    path("dashboard/", AdminDashboardStatsAPIView.as_view(), name="admin-dashboard"),
    path("tickets/", AdminTicketListAPIView.as_view(), name="admin-ticket-list"),
    path("ticket-analytics/", AdminTicketAnalyticsAPIView.as_view(), name="admin-ticket-analytics"),
    path("ai-classification-logs/", AdminAIClassificationLogsAPIView.as_view(), name="admin-ai-classification-logs"),
    path("kb-gaps/", AdminKBGapsAPIView.as_view(), name="admin-kb-gaps"),
    path("reports/summary/", AdminReportSummaryAPIView.as_view(), name="admin-report-summary"),
]