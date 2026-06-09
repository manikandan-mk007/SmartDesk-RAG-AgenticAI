from django.conf import settings
from django.db import models


class FAQ(models.Model):
    class Category(models.TextChoices):
        GENERAL = "GENERAL", "General"
        IT = "IT", "IT Support"
        HR = "HR", "Human Resources"
        FACILITIES = "FACILITIES", "Facilities"

    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.GENERAL,
    )
    tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma separated tags. Example: password, login, vpn",
    )
    is_active = models.BooleanField(default=True)

    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_faqs",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["question"]),
        ]

    def __str__(self):
        return self.question