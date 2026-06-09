from rest_framework import serializers

from .models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
    )

    class Meta:
        model = FAQ
        fields = (
            "id",
            "question",
            "answer",
            "category",
            "tags",
            "is_active",
            "helpful_count",
            "not_helpful_count",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "helpful_count",
            "not_helpful_count",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )


class FAQCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = (
            "id",
            "question",
            "answer",
            "category",
            "tags",
            "is_active",
        )
        read_only_fields = ("id",)

    def validate_question(self, value):
        value = " ".join(value.strip().split())

        if not value:
            raise serializers.ValidationError("FAQ question cannot be empty.")

        return value

    def validate_answer(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("FAQ answer cannot be empty.")

        return value

    def validate_tags(self, value):
        if not value:
            return ""

        tags = [
            tag.strip().lower()
            for tag in value.split(",")
            if tag.strip()
        ]

        return ", ".join(tags)