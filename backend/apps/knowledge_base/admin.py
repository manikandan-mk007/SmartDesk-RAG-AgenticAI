from django.contrib import admin

from .models import KBDocument, KBChunk


class KBChunkInline(admin.TabularInline):
    model = KBChunk
    extra = 0
    readonly_fields = (
        "chunk_index",
        "vector_id",
        "source_title",
        "source_file_name",
        "created_at",
    )


@admin.register(KBDocument)
class KBDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "file_type",
        "status",
        "total_chunks",
        "uploaded_by",
        "created_at",
    )
    list_filter = (
        "file_type",
        "status",
        "created_at",
    )
    search_fields = (
        "title",
        "file",
        "uploaded_by__email",
    )
    readonly_fields = (
        "file_type",
        "status",
        "total_chunks",
        "error_message",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    inlines = [KBChunkInline]


@admin.register(KBChunk)
class KBChunkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "chunk_index",
        "vector_id",
        "created_at",
    )
    list_filter = (
        "created_at",
    )
    search_fields = (
        "chunk_text",
        "source_title",
        "source_file_name",
        "vector_id",
    )
    ordering = ("document", "chunk_index")