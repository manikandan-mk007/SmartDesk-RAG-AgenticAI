from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AdminAgentDetailUpdateAPIView,
    AdminAgentListAPIView,
    AdminCreateAgentAPIView,
    AdminEmployeeRecordListAPIView,
    AdminEmployeeRosterUploadAPIView,
    AdminEmployeeUploadBatchListAPIView,
    AdminRoleTestAPIView,
    AdminUserDetailUpdateAPIView,
    AdminUserListAPIView,
    AdminUserStatusUpdateAPIView,
    AgentProfileAPIView,
    AgentRoleTestAPIView,
    LoginAPIView,
    ProfileAPIView,
    RegisterAPIView,
    UserRoleTestAPIView,
)


urlpatterns = [
    # Public auth APIs
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/profile/", ProfileAPIView.as_view(), name="profile"),

    # Admin APIs
    path("admin/agents/create/", AdminCreateAgentAPIView.as_view(), name="admin-create-agent"),
    path("admin/users/", AdminUserListAPIView.as_view(), name="admin-users-list"),
    path("admin/agents/", AdminAgentListAPIView.as_view(), name="admin-agents-list"),
    path(
        "admin/users/<int:user_id>/status/",
        AdminUserStatusUpdateAPIView.as_view(),
        name="admin-user-status-update",
    ),
    path(
        "admin/users/<int:user_id>/",
        AdminUserDetailUpdateAPIView.as_view(),
        name="admin-user-detail-update",
    ),
    path(
        "admin/agents/<int:agent_id>/",
        AdminAgentDetailUpdateAPIView.as_view(),
        name="admin-agent-detail-update",
    ),

    # Admin employee roster security APIs
    path(
        "admin/employees/upload/",
        AdminEmployeeRosterUploadAPIView.as_view(),
        name="admin-employee-roster-upload",
    ),
    path(
        "admin/employees/",
        AdminEmployeeRecordListAPIView.as_view(),
        name="admin-employee-record-list",
    ),
    path(
        "admin/employees/uploads/",
        AdminEmployeeUploadBatchListAPIView.as_view(),
        name="admin-employee-upload-batch-list",
    ),

    # Agent APIs
    path("agent/profile/", AgentProfileAPIView.as_view(), name="agent-profile"),

    # Role test APIs
    path("role-test/user/", UserRoleTestAPIView.as_view(), name="user-role-test"),
    path("role-test/agent/", AgentRoleTestAPIView.as_view(), name="agent-role-test"),
    path("role-test/admin/", AdminRoleTestAPIView.as_view(), name="admin-role-test"),
]