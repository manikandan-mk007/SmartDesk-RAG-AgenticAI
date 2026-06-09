import os

from rest_framework import serializers

from .models import (
    Ticket,
    TicketAIClassification,
    TicketActivityLog,
    TicketAgentSuggestion,
    TicketAttachment,
    TicketFeedback,
    TicketMessage,
)


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(
        source="sender.full_name",
        read_only=True,
    )

    class Meta:
        model = TicketMessage
        fields = (
            "id",
            "ticket",
            "sender",
            "sender_name",
            "sender_role",
            "message",
            "created_at",
        )
        read_only_fields = (
            "id",
            "ticket",
            "sender",
            "sender_name",
            "sender_role",
            "created_at",
        )


class TicketAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.full_name",
        read_only=True,
    )
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = TicketAttachment
        fields = (
            "id",
            "ticket",
            "uploaded_by",
            "uploaded_by_name",
            "file",
            "file_url",
            "file_type",
            "original_filename",
            "analysis_result",
            "uploaded_at",
        )
        read_only_fields = (
            "id",
            "ticket",
            "uploaded_by",
            "uploaded_by_name",
            "file_url",
            "file_type",
            "original_filename",
            "analysis_result",
            "uploaded_at",
        )

    def get_file_url(self, obj):
        request = self.context.get("request")

        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)

        if obj.file:
            return obj.file.url

        return None


class TicketActivityLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(
        source="performed_by.full_name",
        read_only=True,
    )

    class Meta:
        model = TicketActivityLog
        fields = (
            "id",
            "ticket",
            "performed_by",
            "performed_by_name",
            "action",
            "old_value",
            "new_value",
            "note",
            "created_at",
        )
        read_only_fields = fields

class TicketAIClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAIClassification
        fields = (
            "id",
            "ticket",
            "request_type",
            "priority",
            "sentiment",
            "confidence_score",
            "reason",
            "model_used",
            "created_at",
        )
        read_only_fields = fields

class TicketAgentSuggestionSerializer(serializers.ModelSerializer):
    generated_for_name = serializers.CharField(
        source="generated_for.full_name",
        read_only=True,
    )

    class Meta:
        model = TicketAgentSuggestion
        fields = (
            "id",
            "ticket",
            "generated_for",
            "generated_for_name",
            "ticket_summary",
            "priority_reason",
            "sentiment_explanation",
            "suggested_reply",
            "suggested_steps",
            "escalation_suggestion",
            "related_kb_articles",
            "similar_tickets",
            "model_used",
            "confidence_score",
            "created_at",
        )
        read_only_fields = fields


class TicketFeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.full_name",
        read_only=True,
    )
    agent_name = serializers.CharField(
        source="agent.full_name",
        read_only=True,
    )
    ticket_subject = serializers.CharField(
        source="ticket.subject",
        read_only=True,
    )
    ticket_request_type = serializers.CharField(
        source="ticket.request_type",
        read_only=True,
    )
    ticket_priority = serializers.CharField(
        source="ticket.priority",
        read_only=True,
    )

    class Meta:
        model = TicketFeedback
        fields = (
            "id",
            "ticket",
            "ticket_subject",
            "ticket_request_type",
            "ticket_priority",
            "user",
            "user_name",
            "agent",
            "agent_name",
            "rating",
            "comments",
            "created_at",
        )
        read_only_fields = (
            "id",
            "ticket",
            "ticket_subject",
            "ticket_request_type",
            "ticket_priority",
            "user",
            "user_name",
            "agent",
            "agent_name",
            "created_at",
        )

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class TicketListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.full_name",
        read_only=True,
    )
    assigned_agent_name = serializers.CharField(
        source="assigned_agent.full_name",
        read_only=True,
    )
    status_color = serializers.CharField(read_only=True)
    status_badge_class = serializers.CharField(read_only=True)
    priority_badge_class = serializers.CharField(read_only=True)
    message_count = serializers.IntegerField(
        source="messages.count",
        read_only=True,
    )
    attachment_count = serializers.IntegerField(
        source="attachments.count",
        read_only=True,
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "user",
            "user_name",
            "assigned_agent",
            "assigned_agent_name",
            "subject",
            "description",
            "request_type",
            "priority",
            "status",
            "sentiment",
            "ai_summary",
            "ai_suggested_solution",
            "escalation_required",
            "status_color",
            "status_badge_class",
            "priority_badge_class",
            "message_count",
            "attachment_count",
            "created_at",
            "updated_at",
            "closed_at",
        )
        read_only_fields = fields


class TicketDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.full_name",
        read_only=True,
    )
    assigned_agent_name = serializers.CharField(
        source="assigned_agent.full_name",
        read_only=True,
    )
    messages = TicketMessageSerializer(many=True, read_only=True)
    attachments = TicketAttachmentSerializer(many=True, read_only=True)
    activity_logs = TicketActivityLogSerializer(many=True, read_only=True)
    feedback = TicketFeedbackSerializer(read_only=True)
    ai_classifications = TicketAIClassificationSerializer(many=True, read_only=True)
    agent_suggestions = TicketAgentSuggestionSerializer(many=True, read_only=True)

    status_color = serializers.CharField(read_only=True)
    status_badge_class = serializers.CharField(read_only=True)
    priority_badge_class = serializers.CharField(read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "user",
            "user_name",
            "assigned_agent",
            "assigned_agent_name",
            "subject",
            "description",
            "request_type",
            "priority",
            "status",
            "sentiment",
            "ai_summary",
            "ai_suggested_solution",
            "escalation_required",
            "status_color",
            "status_badge_class",
            "priority_badge_class",
            "messages",
            "attachments",
            "activity_logs",
            "feedback",
            "ai_classifications",
            "agent_suggestions",
            "created_at",
            "updated_at",
            "closed_at",
        )
        read_only_fields = fields


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "subject",
            "description",
        )
        read_only_fields = ("id",)

    def validate_subject(self, value):
        value = " ".join(value.strip().split())

        if not value:
            raise serializers.ValidationError("Subject cannot be empty.")

        return value

    def validate_description(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Description cannot be empty.")

        if len(value) < 10:
            raise serializers.ValidationError(
                "Description must contain at least 10 characters."
            )

        return value

    def create(self, validated_data):
        request = self.context["request"]

        ticket = Ticket.objects.create(
            user=request.user,
            subject=validated_data["subject"],
            description=validated_data["description"],
        )

        TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            sender_role=TicketMessage.SenderRole.USER,
            message=validated_data["description"],
        )

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="TICKET_CREATED",
            new_value=Ticket.Status.OPEN,
            note="Ticket created by user.",
        )

        from apps.ai_engine.ticket_classifier import classify_ticket

        classification = classify_ticket(
            subject=ticket.subject,
            description=ticket.description,
        )

        ticket.request_type = classification["request_type"]
        ticket.priority = classification["priority"]
        ticket.sentiment = classification["sentiment"]
        ticket.ai_summary = classification["summary"]
        ticket.ai_suggested_solution = classification["suggested_solution"]
        ticket.escalation_required = classification["escalation_required"]
        ticket.save(
            update_fields=[
                "request_type",
                "priority",
                "sentiment",
                "ai_summary",
                "ai_suggested_solution",
                "escalation_required",
                "updated_at",
            ]
        )

        TicketAIClassification.objects.create(
            ticket=ticket,
            request_type=classification["request_type"],
            priority=classification["priority"],
            sentiment=classification["sentiment"],
            confidence_score=classification["confidence_score"],
            reason=classification["reason"],
            model_used=classification["model_used"],
        )

        TicketActivityLog.objects.create(
            ticket=ticket,
            performed_by=request.user,
            action="AI_CLASSIFIED",
            new_value=(
                f'{classification["request_type"]} | '
                f'{classification["priority"]} | '
                f'{classification["sentiment"]}'
            ),
            note=classification["reason"],
        )

        return ticket


class TicketMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ("message",)

    def validate_message(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Message cannot be empty.")

        return value


class TicketAttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = ("file",)

    def validate_file(self, value):
        max_size_mb = 25
        max_size_bytes = max_size_mb * 1024 * 1024

        if value.size > max_size_bytes:
            raise serializers.ValidationError(
                f"File size must be less than {max_size_mb}MB."
            )

        allowed_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".mp4",
            ".mov",
            ".avi",
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
        ]

        ext = os.path.splitext(value.name)[1].lower()

        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                "Unsupported file type. Allowed: jpg, jpeg, png, webp, mp4, mov, avi, pdf, doc, docx, txt."
            )

        return value


class StatusOptionsSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
    color = serializers.CharField()
    badge_class = serializers.CharField()

class AgentReplySerializer(serializers.Serializer):
    message = serializers.CharField(min_length=1, max_length=5000)

    def validate_message(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Reply message cannot be empty.")

        return value


class AgentCloseTicketSerializer(serializers.Serializer):
    closing_note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
    )


class AgentEscalateTicketSerializer(serializers.Serializer):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
    )

class AgentFeedbackSummarySerializer(serializers.Serializer):
    average_rating = serializers.FloatField()
    total_feedback = serializers.IntegerField()
    five_star_count = serializers.IntegerField()
    low_rating_count = serializers.IntegerField()


class AdminAgentFeedbackAnalyticsSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField()
    agent_name = serializers.CharField()
    agent_email = serializers.EmailField()
    agent_department = serializers.CharField()
    closed_tickets = serializers.IntegerField()
    feedback_count = serializers.IntegerField()
    average_rating = serializers.FloatField(allow_null=True)
    low_rating_count = serializers.IntegerField()