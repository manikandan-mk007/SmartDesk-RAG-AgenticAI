from django.urls import path

from .views import (
    AdminFAQDetailAPIView,
    AdminFAQListCreateAPIView,
    FAQHelpfulAPIView,
    FAQNotHelpfulAPIView,
    FAQPublicListAPIView,
    FAQSearchAPIView,
)


urlpatterns = [
    # Public FAQ APIs
    path("", FAQPublicListAPIView.as_view(), name="faq-public-list"),
    path("search/", FAQSearchAPIView.as_view(), name="faq-search"),
    path("<int:faq_id>/helpful/", FAQHelpfulAPIView.as_view(), name="faq-helpful"),
    path(
        "<int:faq_id>/not-helpful/",
        FAQNotHelpfulAPIView.as_view(),
        name="faq-not-helpful",
    ),

    # Admin FAQ APIs
    path("admin/", AdminFAQListCreateAPIView.as_view(), name="admin-faq-list-create"),
    path("admin/<int:faq_id>/", AdminFAQDetailAPIView.as_view(), name="admin-faq-detail"),
]