from django.contrib import admin

from .models import (
    Ticket,
    TicketAIClassification,
    TicketActivityLog,
    TicketAgentSuggestion,
    TicketAttachment,
    TicketFeedback,
    TicketMessage,
)


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ("created_at",)


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    readonly_fields = ("uploaded_at",)


class TicketActivityLogInline(admin.TabularInline):
    model = TicketActivityLog
    extra = 0
    readonly_fields = ("created_at",)

class TicketAIClassificationInline(admin.TabularInline):
    model = TicketAIClassification
    extra = 0
    readonly_fields = ("created_at",)

class TicketAgentSuggestionInline(admin.TabularInline):
    model = TicketAgentSuggestion
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject",
        "user",
        "assigned_agent",
        "request_type",
        "priority",
        "status",
        "sentiment",
        "created_at",
    )
    list_filter = (
        "request_type",
        "priority",
        "status",
        "sentiment",
        "created_at",
    )
    search_fields = (
        "subject",
        "description",
        "user__email",
        "user__full_name",
        "assigned_agent__email",
        "assigned_agent__full_name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "closed_at",
    )
    ordering = ("-created_at",)
    inlines = [
        TicketMessageInline,
        TicketAttachmentInline,
        TicketActivityLogInline,
        TicketAIClassificationInline,
        TicketAgentSuggestionInline,
    ]


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "sender",
        "sender_role",
        "created_at",
    )
    list_filter = (
        "sender_role",
        "created_at",
    )
    search_fields = (
        "message",
        "ticket__subject",
        "sender__email",
    )
    ordering = ("-created_at",)


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "uploaded_by",
        "file_type",
        "original_filename",
        "uploaded_at",
    )
    list_filter = (
        "file_type",
        "uploaded_at",
    )
    search_fields = (
        "original_filename",
        "ticket__subject",
        "uploaded_by__email",
    )
    ordering = ("-uploaded_at",)


@admin.register(TicketActivityLog)
class TicketActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "performed_by",
        "action",
        "old_value",
        "new_value",
        "created_at",
    )
    list_filter = (
        "action",
        "created_at",
    )
    search_fields = (
        "ticket__subject",
        "performed_by__email",
        "action",
        "note",
    )
    ordering = ("-created_at",)


@admin.register(TicketFeedback)
class TicketFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "user",
        "rating",
        "created_at",
    )
    list_filter = (
        "rating",
        "created_at",
    )
    search_fields = (
        "ticket__subject",
        "user__email",
        "comments",
    )
    ordering = ("-created_at",)

@admin.register(TicketAIClassification)
class TicketAIClassificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "request_type",
        "priority",
        "sentiment",
        "confidence_score",
        "model_used",
        "created_at",
    )
    list_filter = (
        "request_type",
        "priority",
        "sentiment",
        "model_used",
        "created_at",
    )
    search_fields = (
        "ticket__subject",
        "reason",
        "model_used",
    )
    ordering = ("-created_at",)

@admin.register(TicketAgentSuggestion)
class TicketAgentSuggestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "generated_for",
        "model_used",
        "confidence_score",
        "created_at",
    )
    list_filter = (
        "model_used",
        "created_at",
    )
    search_fields = (
        "ticket__subject",
        "ticket_summary",
        "suggested_reply",
        "suggested_steps",
    )
    ordering = ("-created_at",)