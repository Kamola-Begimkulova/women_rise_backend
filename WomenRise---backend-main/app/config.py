"""Application configuration. Values can be overridden via environment variables."""
import os

# Security
SECRET_KEY = os.getenv("WOMENRISE_SECRET", "womenrise-dev-secret-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Database — SQLite locally; set WOMENRISE_DB to a Postgres URL in production.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv("WOMENRISE_DB", f"sqlite:///{os.path.join(BASE_DIR, 'womenrise.db')}")

# Render hands out "postgres://"; SQLAlchemy 2 needs the "postgresql://" scheme.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# CORS — local dev origins plus any set via WOMENRISE_CORS (comma-separated)
_DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://localhost:3000",
]
_extra = [o.strip() for o in os.getenv("WOMENRISE_CORS", "").split(",") if o.strip()]
CORS_ORIGINS = _DEFAULT_ORIGINS + _extra

# Allow Vercel/Netlify preview + production subdomains without listing each one.
CORS_ORIGIN_REGEX = os.getenv(
    "WOMENRISE_CORS_REGEX",
    r"https://.*\.(vercel\.app|netlify\.app|onrender\.com)",
)
