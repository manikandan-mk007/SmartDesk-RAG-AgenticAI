import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_list(key: str, default: str = "") -> list[str]:
    value = os.getenv(key, default)
    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-smart-service-desk-dev-key",
)

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")


INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",

    # Local apps
    "apps.core",
    "apps.accounts",
    "apps.tickets",
    "apps.faqs",
    "apps.knowledge_base",
    "apps.ai_engine",
    "apps.dashboard",
    "apps.notifications",
]


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_USER_MODEL = "accounts.User"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

CORS_ALLOW_CREDENTIALS = True


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# AI / LLM SETTINGS
# Provider options: auto, groq, openrouter, rules
# auto order: Groq primary -> Groq fallback -> OpenRouter primary -> OpenRouter fallback -> rules
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").lower()

# Gemini disabled, kept only for old code compatibility
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "")

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

GROQ_PRIMARY_MODEL = os.getenv(
    "GROQ_PRIMARY_MODEL",
    "llama-3.3-70b-versatile",
)

GROQ_FALLBACK_MODEL = os.getenv(
    "GROQ_FALLBACK_MODEL",
    "llama-3.1-8b-instant",
)

# Old code compatibility: if any old service uses settings.GROQ_MODEL,
# it will use the primary Groq model.
GROQ_MODEL = os.getenv("GROQ_MODEL", GROQ_PRIMARY_MODEL)

# OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.3-70b-instruct:free",
)

OPENROUTER_FALLBACK_MODEL = os.getenv(
    "OPENROUTER_FALLBACK_MODEL",
    "deepseek/deepseek-r1:free",
)

AI_TIMEOUT_SECONDS = int(os.getenv("AI_TIMEOUT_SECONDS", "30"))

# RAG / VECTOR DB SETTINGS
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

CHROMA_DB_PATH = BASE_DIR / os.getenv(
    "CHROMA_DB_PATH",
    "./data/vector_store/chroma_db",
)

CHROMA_COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "smartdesk_kb_chunks",
)

RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.25"))

# IMAGE / VIDEO PROCESSING SETTINGS
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")

IMAGE_ANALYSIS_ENABLED = os.getenv("IMAGE_ANALYSIS_ENABLED", "True") == "True"
VIDEO_ANALYSIS_ENABLED = os.getenv("VIDEO_ANALYSIS_ENABLED", "True") == "True"

VIDEO_MAX_FRAMES = int(os.getenv("VIDEO_MAX_FRAMES", "5"))

KB_CLEAN_TEXT_ENABLED = os.getenv("KB_CLEAN_TEXT_ENABLED", "True") == "True"
KB_CHUNK_MAX_WORDS = int(os.getenv("KB_CHUNK_MAX_WORDS", "220"))
KB_CHUNK_OVERLAP_WORDS = int(os.getenv("KB_CHUNK_OVERLAP_WORDS", "35"))
KB_SPLIT_BY_ISSUE = os.getenv("KB_SPLIT_BY_ISSUE", "True") == "True"