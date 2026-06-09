from django.contrib import admin

from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question",
        "category",
        "is_active",
        "helpful_count",
        "not_helpful_count",
        "created_by",
        "created_at",
    )
    list_filter = (
        "category",
        "is_active",
        "created_at",
    )
    search_fields = (
        "question",
        "answer",
        "tags",
    )
    readonly_fields = (
        "helpful_count",
        "not_helpful_count",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)