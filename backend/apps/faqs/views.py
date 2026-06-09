from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole

from .models import FAQ
from .serializers import FAQCreateUpdateSerializer, FAQSerializer


class FAQPublicListAPIView(generics.ListAPIView):
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return FAQ.objects.filter(is_active=True).order_by("-created_at")


class FAQSearchAPIView(generics.ListAPIView):
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = FAQ.objects.filter(is_active=True)

        query = self.request.query_params.get("q", "").strip()
        category = self.request.query_params.get("category", "").strip().upper()

        if query:
            queryset = queryset.filter(
                Q(question__icontains=query)
                | Q(answer__icontains=query)
                | Q(tags__icontains=query)
                | Q(category__icontains=query)
            )

        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by("-helpful_count", "-created_at")


class FAQHelpfulAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, faq_id):
        try:
            faq = FAQ.objects.get(id=faq_id, is_active=True)
        except FAQ.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "FAQ not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        faq.helpful_count += 1
        faq.save(update_fields=["helpful_count"])

        return Response(
            {
                "status": "success",
                "message": "Thank you for your feedback.",
                "faq_id": faq.id,
                "helpful_count": faq.helpful_count,
                "not_helpful_count": faq.not_helpful_count,
            },
            status=status.HTTP_200_OK,
        )


class FAQNotHelpfulAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, faq_id):
        try:
            faq = FAQ.objects.get(id=faq_id, is_active=True)
        except FAQ.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "FAQ not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        faq.not_helpful_count += 1
        faq.save(update_fields=["not_helpful_count"])

        return Response(
            {
                "status": "success",
                "message": "Thank you for your feedback.",
                "faq_id": faq.id,
                "helpful_count": faq.helpful_count,
                "not_helpful_count": faq.not_helpful_count,
            },
            status=status.HTTP_200_OK,
        )


class AdminFAQListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        queryset = FAQ.objects.all()

        category = self.request.query_params.get("category", "").strip().upper()
        is_active = self.request.query_params.get("is_active", "").strip().lower()
        query = self.request.query_params.get("q", "").strip()

        if category:
            queryset = queryset.filter(category=category)

        if is_active in ["true", "false"]:
            queryset = queryset.filter(is_active=is_active == "true")

        if query:
            queryset = queryset.filter(
                Q(question__icontains=query)
                | Q(answer__icontains=query)
                | Q(tags__icontains=query)
            )

        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return FAQCreateUpdateSerializer

        return FAQSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        faq = serializer.save(created_by=request.user)

        return Response(
            {
                "status": "success",
                "message": "FAQ created successfully.",
                "faq": FAQSerializer(faq).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminFAQDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQ.objects.all()
    permission_classes = [IsAdminRole]
    lookup_url_kwarg = "faq_id"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return FAQCreateUpdateSerializer

        return FAQSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        faq = self.get_object()

        serializer = self.get_serializer(
            faq,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        updated_faq = serializer.save()

        return Response(
            {
                "status": "success",
                "message": "FAQ updated successfully.",
                "faq": FAQSerializer(updated_faq).data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        faq = self.get_object()
        faq.delete()

        return Response(
            {
                "status": "success",
                "message": "FAQ deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )