import os
import uuid

from django.conf import settings
from django.db import models


def ticket_attachment_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("ticket_attachments", str(instance.ticket.id), unique_filename)


class Ticket(models.Model):
    class RequestType(models.TextChoices):
        UNASSIGNED = "UNASSIGNED", "Unassigned"
        IT = "IT", "IT"
        HR = "HR", "HR"
        FACILITIES = "FACILITIES", "Facilities"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        CLOSED = "CLOSED", "Closed"
        ESCALATED = "ESCALATED", "Escalated"

    class Sentiment(models.TextChoices):
        NEUTRAL = "NEUTRAL", "Neutral"
        CALM = "CALM", "Calm"
        CONFUSED = "CONFUSED", "Confused"
        FRUSTRATED = "FRUSTRATED", "Frustrated"
        ANGRY = "ANGRY", "Angry"
        URGENT = "URGENT", "Urgent"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )

    subject = models.CharField(max_length=255)
    description = models.TextField()

    request_type = models.CharField(
        max_length=30,
        choices=RequestType.choices,
        default=RequestType.UNASSIGNED,
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.OPEN,
    )
    sentiment = models.CharField(
        max_length=30,
        choices=Sentiment.choices,
        default=Sentiment.NEUTRAL,
    )

    ai_summary = models.TextField(blank=True)
    ai_suggested_solution = models.TextField(blank=True)
    escalation_required = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["request_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"#{self.id} - {self.subject}"

    @property
    def status_color(self):
        colors = {
            self.Status.OPEN: "red",
            self.Status.IN_PROGRESS: "yellow",
            self.Status.CLOSED: "green",
            self.Status.ESCALATED: "purple",
        }
        return colors.get(self.status, "gray")

    @property
    def status_badge_class(self):
        classes = {
            self.Status.OPEN: "bg-red-100 text-red-700 border-red-200",
            self.Status.IN_PROGRESS: "bg-yellow-100 text-yellow-700 border-yellow-200",
            self.Status.CLOSED: "bg-green-100 text-green-700 border-green-200",
            self.Status.ESCALATED: "bg-purple-100 text-purple-700 border-purple-200",
        }
        return classes.get(self.status, "bg-gray-100 text-gray-700 border-gray-200")

    @property
    def priority_badge_class(self):
        classes = {
            self.Priority.HIGH: "bg-red-100 text-red-700 border-red-200",
            self.Priority.MEDIUM: "bg-yellow-100 text-yellow-700 border-yellow-200",
            self.Priority.LOW: "bg-green-100 text-green-700 border-green-200",
        }
        return classes.get(self.priority, "bg-gray-100 text-gray-700 border-gray-200")


class TicketMessage(models.Model):
    class SenderRole(models.TextChoices):
        USER = "USER", "User"
        AGENT = "AGENT", "Agent"
        ADMIN = "ADMIN", "Admin"
        AI = "AI", "AI"

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_messages",
    )
    sender_role = models.CharField(
        max_length=20,
        choices=SenderRole.choices,
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.ticket.id} - {self.sender_role}"


class TicketAttachment(models.Model):
    class FileType(models.TextChoices):
        IMAGE = "IMAGE", "Image"
        VIDEO = "VIDEO", "Video"
        DOCUMENT = "DOCUMENT", "Document"
        OTHER = "OTHER", "Other"

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_attachments",
    )
    file = models.FileField(upload_to=ticket_attachment_upload_path)
    file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.OTHER,
    )
    original_filename = models.CharField(max_length=255, blank=True)
    analysis_result = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.ticket.id} - {self.file_type}"


class TicketActivityLog(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_activities",
    )
    action = models.CharField(max_length=100)
    old_value = models.CharField(max_length=255, blank=True)
    new_value = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket.id} - {self.action}"


class TicketFeedback(models.Model):
    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ticket_feedbacks",
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_ticket_feedbacks",
    )
    rating = models.PositiveSmallIntegerField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["rating"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        agent_name = self.agent.full_name if self.agent else "No Agent"
        return f"Ticket #{self.ticket.id} - {agent_name} - Rating {self.rating}"
    
class TicketAIClassification(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="ai_classifications",
    )
    request_type = models.CharField(max_length=30)
    priority = models.CharField(max_length=20)
    sentiment = models.CharField(max_length=30)
    confidence_score = models.FloatField(default=0.0)
    reason = models.TextField(blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ticket #{self.ticket.id} - {self.model_used}"
    
class TicketAgentSuggestion(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="agent_suggestions",
    )
    generated_for = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_agent_suggestions",
    )

    ticket_summary = models.TextField(blank=True)
    priority_reason = models.TextField(blank=True)
    sentiment_explanation = models.TextField(blank=True)
    suggested_reply = models.TextField()
    suggested_steps = models.TextField(blank=True)
    escalation_suggestion = models.TextField(blank=True)

    related_kb_articles = models.JSONField(default=list, blank=True)
    similar_tickets = models.JSONField(default=list, blank=True)

    model_used = models.CharField(max_length=100, blank=True)
    confidence_score = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Suggestion for Ticket #{self.ticket.id}"