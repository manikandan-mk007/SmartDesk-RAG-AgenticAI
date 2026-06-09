from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .employee_services import process_employee_roster
from .models import EmployeeRecord, EmployeeUploadBatch
from .permissions import IsAdminRole, IsAgentRole, IsUserRole
from .serializers import (
    AdminAgentUpdateSerializer,
    AdminCreateAgentSerializer,
    AdminUserListSerializer,
    AdminUserUpdateSerializer,
    AgentProfileSerializer,
    CustomTokenObtainPairSerializer,
    EmployeeRecordSerializer,
    EmployeeRosterUploadSerializer,
    EmployeeUploadBatchSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    UserStatusUpdateSerializer,
)


User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "status": "success",
                "message": "Account created successfully.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)

        return Response(
            {
                "status": "success",
                "message": "Profile fetched successfully.",
                "user": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class AdminCreateAgentAPIView(generics.CreateAPIView):
    serializer_class = AdminCreateAgentSerializer
    permission_classes = [IsAdminRole]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agent = serializer.save()

        return Response(
            {
                "status": "success",
                "message": "Agent created successfully.",
                "agent": AdminUserListSerializer(agent).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminUserListAPIView(generics.ListAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return User.objects.all().order_by("-date_joined")


class AdminAgentListAPIView(generics.ListAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return User.objects.filter(role=User.Role.AGENT).order_by("-date_joined")


class AdminUserStatusUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserStatusUpdateSerializer
    permission_classes = [IsAdminRole]
    lookup_url_kwarg = "user_id"

    def get_queryset(self):
        return User.objects.all()

    def patch(self, request, *args, **kwargs):
        user = self.get_object()

        if user.role == User.Role.ADMIN and user.id == request.user.id:
            return Response(
                {
                    "status": "error",
                    "message": "You cannot deactivate your own admin account.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "status": "success",
                "message": "User status updated successfully.",
                "user": AdminUserListSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class AgentProfileAPIView(APIView):
    permission_classes = [IsAgentRole]

    def get(self, request):
        serializer = AgentProfileSerializer(request.user)

        return Response(
            {
                "status": "success",
                "message": "Agent profile fetched successfully.",
                "agent": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UserRoleTestAPIView(APIView):
    permission_classes = [IsUserRole]

    def get(self, request):
        return Response(
            {
                "status": "success",
                "message": "USER role access verified.",
                "user": {
                    "id": request.user.id,
                    "email": request.user.email,
                    "employee_id": request.user.employee_id,
                    "role": request.user.role,
                },
            },
            status=status.HTTP_200_OK,
        )


class AgentRoleTestAPIView(APIView):
    permission_classes = [IsAgentRole]

    def get(self, request):
        return Response(
            {
                "status": "success",
                "message": "AGENT role access verified.",
                "user": {
                    "id": request.user.id,
                    "email": request.user.email,
                    "employee_id": request.user.employee_id,
                    "role": request.user.role,
                },
            },
            status=status.HTTP_200_OK,
        )


class AdminRoleTestAPIView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response(
            {
                "status": "success",
                "message": "ADMIN role access verified.",
                "user": {
                    "id": request.user.id,
                    "email": request.user.email,
                    "employee_id": request.user.employee_id,
                    "role": request.user.role,
                },
            },
            status=status.HTTP_200_OK,
        )


class AdminUserDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminRole]
    lookup_url_kwarg = "user_id"

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AdminUserUpdateSerializer

        return AdminUserListSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        user = self.get_object()

        if user.role == User.Role.ADMIN and user.id == request.user.id:
            if "is_active" in request.data and request.data.get("is_active") is False:
                return Response(
                    {
                        "status": "error",
                        "message": "You cannot deactivate your own admin account.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "status": "success",
                "message": "User updated successfully.",
                "user": AdminUserListSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class AdminAgentDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminRole]
    lookup_url_kwarg = "agent_id"

    def get_queryset(self):
        return User.objects.filter(role=User.Role.AGENT)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AdminAgentUpdateSerializer

        return AdminUserListSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        agent = self.get_object()

        serializer = self.get_serializer(
            agent,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "status": "success",
                "message": "Agent updated successfully.",
                "agent": AdminUserListSerializer(agent).data,
            },
            status=status.HTTP_200_OK,
        )


class AdminEmployeeRosterUploadAPIView(generics.CreateAPIView):
    serializer_class = EmployeeRosterUploadSerializer
    permission_classes = [IsAdminRole]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        batch = EmployeeUploadBatch.objects.create(
            file=serializer.validated_data["file"],
            uploaded_by=request.user,
            status=EmployeeUploadBatch.Status.PROCESSING,
        )

        batch = process_employee_roster(batch)

        response_status = (
            status.HTTP_201_CREATED
            if batch.status == EmployeeUploadBatch.Status.COMPLETED
            else status.HTTP_400_BAD_REQUEST
        )

        return Response(
            {
                "status": "success"
                if batch.status == EmployeeUploadBatch.Status.COMPLETED
                else "error",
                "message": "Employee roster processed successfully."
                if batch.status == EmployeeUploadBatch.Status.COMPLETED
                else "Employee roster processing failed.",
                "batch": EmployeeUploadBatchSerializer(
                    batch,
                    context={"request": request},
                ).data,
            },
            status=response_status,
        )


class AdminEmployeeRecordListAPIView(generics.ListAPIView):
    serializer_class = EmployeeRecordSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        queryset = EmployeeRecord.objects.select_related(
            "registered_user",
            "upload_batch",
        ).all()

        status_filter = self.request.query_params.get("status")
        role_type = self.request.query_params.get("role_type")
        search = self.request.query_params.get("search")

        if status_filter == "active":
            queryset = queryset.filter(is_active=True)
        elif status_filter == "inactive":
            queryset = queryset.filter(is_active=False)

        if role_type:
            queryset = queryset.filter(role_type=role_type.upper())

        if search:
            queryset = queryset.filter(
                employee_id__icontains=search
            ) | queryset.filter(
                full_name__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )

        return queryset.order_by("employee_id")


class AdminEmployeeUploadBatchListAPIView(generics.ListAPIView):
    serializer_class = EmployeeUploadBatchSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return EmployeeUploadBatch.objects.select_related("uploaded_by").all()