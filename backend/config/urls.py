from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from apps.knowledge_base.views import RAGAskAPIView, CreateTicketFromRAGAPIView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("apps.core.urls")),
    path("api/", include("apps.accounts.urls")),
    path("api/faqs/", include("apps.faqs.urls")),
    path("api/tickets/", include("apps.tickets.urls")),
    path("api/kb/", include("apps.knowledge_base.urls")),
    
    #RAG ask
    path("api/rag/ask/", RAGAskAPIView.as_view(), name="rag-ask"),
    path("api/rag/create-ticket/", CreateTicketFromRAGAPIView.as_view(), name="rag-create-ticket"),

    # Agent dashboard and queue APIs
    path("api/agent/", include("apps.dashboard.urls")),
    path("api/agent/", include("apps.tickets.agent_urls")),

    # Admin dashboard, analytics, logs, reports
    path("api/admin/", include("apps.dashboard.admin_urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)