from __future__ import annotations

import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///taskassigner.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Auth/session policy
    SESSION_TTL_HOURS = {
        "crew": 12,
        "shift_lead": 8,
        "manager": 8,
        "owner": 24,
    }
    DEFAULT_SESSION_TTL = timedelta(hours=8)

    LOCKOUT_THRESHOLD = 5
    LOCKOUT_MINUTES = 15
    AUTH_RATE_LIMIT_PER_MINUTE = 5
    PASSWORD_RESET_TOKEN_MINUTES = int(os.getenv("PASSWORD_RESET_TOKEN_MINUTES", "30"))

    # Email delivery configuration (recipient is runtime-configurable in app settings)
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    EMAIL_FROM = os.getenv("EMAIL_FROM", "")

    # Structured logging baseline
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
