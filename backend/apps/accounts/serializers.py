from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .employee_services import (
    EmployeeRosterProcessingError,
    validate_employee_can_login,
    validate_employee_can_register,
)
from .models import EmployeeRecord, EmployeeUploadBatch


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "employee_id",
            "role",
            "is_active",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "role",
            "is_active",
            "date_joined",
        )


class RegisterSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=50,
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "employee_id",
            "password",
            "confirm_password",
        )
        read_only_fields = ("id",)

    def validate_email(self, value):
        value = value.lower().strip()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")

        return value

    def validate_employee_id(self, value):
        value = value.strip().upper()

        if User.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("This employee ID is already registered.")

        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        employee_id = attrs.get("employee_id")
        email = attrs.get("email")

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Password and confirm password do not match."}
            )

        validate_password(password)

        try:
            employee_record = validate_employee_can_register(
                employee_id=employee_id,
                email=email,
            )
        except EmployeeRosterProcessingError as exc:
            raise serializers.ValidationError({"employee_id": str(exc)})

        if employee_record.role_type != EmployeeRecord.RoleType.USER:
            raise serializers.ValidationError(
                {
                    "employee_id": (
                        "This employee ID is not allowed for normal user registration."
                    )
                }
            )

        attrs["employee_record"] = employee_record
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        employee_record = validated_data.pop("employee_record")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data["full_name"],
            employee_id=validated_data["employee_id"],
            role=User.Role.USER,
            is_active=True,
        )

        employee_record.registered_user = user
        employee_record.save(update_fields=["registered_user", "updated_at"])

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

        try:
            validate_employee_can_login(user)
        except EmployeeRosterProcessingError as exc:
            raise serializers.ValidationError(str(exc))

        data["user"] = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "employee_id": user.employee_id,
            "role": user.role,
            "is_active": user.is_active,
        }

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["user_id"] = user.id
        token["email"] = user.email
        token["full_name"] = user.full_name
        token["employee_id"] = user.employee_id or ""
        token["role"] = user.role

        return token


class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "employee_id",
            "role",
            "is_active",
            "is_staff",
            "date_joined",
        )


class AdminCreateAgentSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=50,
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "employee_id",
            "password",
            "confirm_password",
            "is_active",
        )
        read_only_fields = ("id",)

    def validate_email(self, value):
        value = value.lower().strip()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")

        return value

    def validate_employee_id(self, value):
        value = value.strip().upper()

        if User.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("This employee ID is already registered.")

        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        employee_id = attrs.get("employee_id")
        email = attrs.get("email")

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Password and confirm password do not match."}
            )

        validate_password(password)

        try:
            employee_record = validate_employee_can_register(
                employee_id=employee_id,
                email=email,
            )
        except EmployeeRosterProcessingError as exc:
            raise serializers.ValidationError({"employee_id": str(exc)})

        if employee_record.role_type != EmployeeRecord.RoleType.AGENT:
            raise serializers.ValidationError(
                {
                    "employee_id": (
                        "This employee ID is not allowed for agent account creation."
                    )
                }
            )

        attrs["employee_record"] = employee_record
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        employee_record = validated_data.pop("employee_record")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data["full_name"],
            employee_id=validated_data["employee_id"],
            role=User.Role.AGENT,
            is_active=validated_data.get("is_active", True),
        )

        employee_record.registered_user = user
        employee_record.save(update_fields=["registered_user", "updated_at"])

        return user


class UserStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("is_active",)

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save(update_fields=["is_active"])
        return instance


class AgentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "employee_id",
            "role",
            "is_active",
            "date_joined",
        )
        read_only_fields = fields


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "full_name",
            "email",
            "is_active",
        )

    def validate_email(self, value):
        value = value.lower().strip()

        user_id = self.instance.id if self.instance else None

        if User.objects.exclude(id=user_id).filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already used by another user."
            )

        return value


class AdminAgentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "full_name",
            "email",
            "is_active",
        )

    def validate_email(self, value):
        value = value.lower().strip()

        user_id = self.instance.id if self.instance else None

        if User.objects.exclude(id=user_id).filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already used by another user."
            )

        return value


class EmployeeRecordSerializer(serializers.ModelSerializer):
    registered_user_name = serializers.CharField(
        source="registered_user.full_name",
        read_only=True,
    )
    registered_user_email = serializers.CharField(
        source="registered_user.email",
        read_only=True,
    )

    class Meta:
        model = EmployeeRecord
        fields = (
            "id",
            "employee_id",
            "full_name",
            "email",
            "department",
            "role_type",
            "is_active",
            "registered_user",
            "registered_user_name",
            "registered_user_email",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class EmployeeUploadBatchSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.full_name",
        read_only=True,
    )
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeUploadBatch
        fields = (
            "id",
            "file",
            "file_url",
            "uploaded_by",
            "uploaded_by_name",
            "status",
            "total_records",
            "active_records",
            "inactive_records",
            "error_message",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_file_url(self, obj):
        request = self.context.get("request")

        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)

        if obj.file:
            return obj.file.url

        return None


class EmployeeRosterUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeUploadBatch
        fields = ("file",)

    def validate_file(self, value):
        max_size_mb = 5
        max_size_bytes = max_size_mb * 1024 * 1024

        if value.size > max_size_bytes:
            raise serializers.ValidationError(
                f"File size must be less than {max_size_mb}MB."
            )

        file_name = value.name.lower()

        if not file_name.endswith(".csv"):
            raise serializers.ValidationError(
                "Only CSV file upload is supported."
            )

        return value