import os

from rest_framework import serializers

from .models import KBDocument, KBChunk


class KBChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBChunk
        fields = (
            "id",
            "document",
            "chunk_text",
            "chunk_index",
            "vector_id",
            "source_title",
            "source_file_name",
            "created_at",
        )
        read_only_fields = fields


class KBDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.full_name",
        read_only=True,
    )
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = KBDocument
        fields = (
            "id",
            "title",
            "file",
            "file_url",
            "file_type",
            "uploaded_by",
            "uploaded_by_name",
            "status",
            "total_chunks",
            "error_message",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "file_url",
            "file_type",
            "uploaded_by",
            "uploaded_by_name",
            "status",
            "total_chunks",
            "error_message",
            "created_at",
            "updated_at",
        )

    def get_file_url(self, obj):
        request = self.context.get("request")

        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)

        if obj.file:
            return obj.file.url

        return None


class KBDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBDocument
        fields = (
            "title",
            "file",
        )

    def validate_title(self, value):
        value = " ".join(value.strip().split())

        if not value:
            raise serializers.ValidationError("Document title is required.")

        return value

    def validate_file(self, value):
        max_size_mb = 15
        max_size_bytes = max_size_mb * 1024 * 1024

        if value.size > max_size_bytes:
            raise serializers.ValidationError(
                f"File size must be less than {max_size_mb}MB."
            )

        allowed_extensions = [".pdf", ".txt", ".docx"]
        ext = os.path.splitext(value.name)[1].lower()

        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                "Unsupported file type. Allowed file types: PDF, TXT, DOCX."
            )

        return value

class RAGChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField()


class RAGAskSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, allow_blank=False)
    session_id = serializers.CharField(required=False, allow_blank=True)
    chat_history = RAGChatMessageSerializer(many=True, required=False)


class CreateTicketFromRAGSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, allow_blank=False)
    rag_answer = serializers.CharField(required=False, allow_blank=True)
    subject = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    session_id = serializers.CharField(required=False, allow_blank=True)
    conversation = RAGChatMessageSerializer(many=True, required=False)

