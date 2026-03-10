# ============================================================
# PatosGym — Production Dockerfile
# Optimized for security, minimal attack surface, and WebP
# ============================================================

FROM python:3.11-slim AS base

# ── Build-time variables
ARG APP_USER=appuser
ARG APP_HOME=/app

# ── Python runtime env
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ── System dependencies
#    libwebp-dev  → Pillow WebP support (for load_initial_images command)
#    libpq-dev    → psycopg2 compile dependency
#    gcc          → C compiler for psycopg2-binary native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        libwebp-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Create non-root application user (security hardening)
RUN groupadd --gid 1001 ${APP_USER} \
    && useradd --uid 1001 --gid ${APP_USER} --shell /bin/bash \
               --create-home --no-log-init ${APP_USER}

# ── Working directory
WORKDIR ${APP_HOME}

# ── Install Python dependencies (separate layer for better cache)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ── Copy application source AFTER deps (cache layer order matters)
COPY --chown=${APP_USER}:${APP_USER} . .

# ── Create runtime directories and set ownership
#    Volumes will be bind-mounted at these paths from the host.
RUN mkdir -p ${APP_HOME}/staticfiles ${APP_HOME}/media ${APP_HOME}/logs && \
    chown -R ${APP_USER}:${APP_USER} ${APP_HOME}

# ── Entrypoint
COPY --chown=${APP_USER}:${APP_USER} docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# ── Run as non-root
USER ${APP_USER}

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
# 4 workers = (2 × CPU_count) + 1 for a typical 2-core VPS
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--log-level", "info", \
     "--access-logfile", "/app/logs/gunicorn_access.log", \
     "--error-logfile",  "/app/logs/gunicorn_error.log", \
     "patosgym_project.wsgi:application"]
