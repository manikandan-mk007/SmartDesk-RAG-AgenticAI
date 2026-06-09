import os
import uuid

from django.conf import settings
from django.db import models


def kb_document_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("kb_documents", unique_filename)


class KBDocument(models.Model):
    class FileType(models.TextChoices):
        PDF = "PDF", "PDF"
        TXT = "TXT", "Text"
        DOCX = "DOCX", "Word Document"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=kb_document_upload_path)
    file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.OTHER,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_kb_documents",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PROCESSING,
    )
    total_chunks = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["file_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title


class KBChunk(models.Model):
    document = models.ForeignKey(
        KBDocument,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    chunk_text = models.TextField()
    chunk_index = models.PositiveIntegerField()
    vector_id = models.CharField(max_length=255, unique=True)
    source_title = models.CharField(max_length=255, blank=True)
    source_file_name = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["chunk_index"]
        indexes = [
            models.Index(fields=["document", "chunk_index"]),
            models.Index(fields=["vector_id"]),
        ]

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"