from django.urls import path

from .views import (
    CreateTicketFromRAGAPIView,
    KBDocumentDetailAPIView,
    KBDocumentListAPIView,
    KBDocumentUploadAPIView,
    RAGAskAPIView,
)


urlpatterns = [
    path("documents/upload/", KBDocumentUploadAPIView.as_view(), name="kb-document-upload"),
    path("documents/", KBDocumentListAPIView.as_view(), name="kb-document-list"),
    path(
        "documents/<int:document_id>/",
        KBDocumentDetailAPIView.as_view(),
        name="kb-document-detail",
    ),

    path("rag/ask/", RAGAskAPIView.as_view(), name="rag-ask"),
    path(
        "rag/create-ticket/",
        CreateTicketFromRAGAPIView.as_view(),
        name="rag-create-ticket",
    ),
]