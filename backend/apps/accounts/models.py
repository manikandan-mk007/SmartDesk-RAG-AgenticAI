from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "USER", "User"
        AGENT = "AGENT", "Agent"
        ADMIN = "ADMIN", "Admin"

    username = None
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} - {self.email}"
    

import os
import uuid
from django.conf import settings
from django.db import models


def employee_roster_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("employee_rosters", unique_filename)


class EmployeeUploadBatch(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    file = models.FileField(upload_to=employee_roster_upload_path)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_roster_uploads",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PROCESSING,
    )
    total_records = models.PositiveIntegerField(default=0)
    active_records = models.PositiveIntegerField(default=0)
    inactive_records = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Employee Upload Batch #{self.id}"


class EmployeeRecord(models.Model):
    class RoleType(models.TextChoices):
        USER = "USER", "User"
        AGENT = "AGENT", "Agent"
        ADMIN = "ADMIN", "Admin"

    employee_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    department = models.CharField(max_length=100, blank=True)
    role_type = models.CharField(
        max_length=20,
        choices=RoleType.choices,
        default=RoleType.USER,
    )
    is_active = models.BooleanField(default=True)

    upload_batch = models.ForeignKey(
        EmployeeUploadBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_records",
    )

    registered_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_record",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee_id"]
        indexes = [
            models.Index(fields=["employee_id"]),
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["role_type"]),
        ]

    def __str__(self):
        return f"{self.employee_id} - {self.full_name or self.email}"