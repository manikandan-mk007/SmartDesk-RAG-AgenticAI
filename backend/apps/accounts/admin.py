from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import EmployeeRecord, EmployeeUploadBatch
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "id",
        "email",
        "full_name",
        "role",
        "is_active",
        "is_staff",
        "created_at_display",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "email",
        "full_name",
    )

    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Information",
            {
                "fields": (
                    "full_name",
                    "first_name",
                    "last_name",
                    "role",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "role",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    readonly_fields = ("last_login", "date_joined")

    def created_at_display(self, obj):
        return obj.date_joined

    created_at_display.short_description = "Created At"

@admin.register(EmployeeRecord)
class EmployeeRecordAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "full_name",
        "email",
        "department",
        "role_type",
        "is_active",
        "registered_user",
    )
    list_filter = ("is_active", "role_type", "department")
    search_fields = ("employee_id", "full_name", "email")


@admin.register(EmployeeUploadBatch)
class EmployeeUploadBatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "total_records",
        "active_records",
        "inactive_records",
        "uploaded_by",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("id",)