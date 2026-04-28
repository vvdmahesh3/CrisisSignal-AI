# ────────────────────────────────────────────────────────────────────
# CrisisSignal AI — Dockerfile
# Phase 4: Production-grade multi-stage build
#
# Stage 1 (builder): installs Python deps into a venv
# Stage 2 (runtime): copies only the venv + app code — no build tools
# Result: ~30% smaller final image compared to single-stage
# ────────────────────────────────────────────────────────────────────

# ── Stage 1: Dependency Builder ──────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies (needed for Pillow, scikit-learn wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create isolated venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (cached layer if requirements unchanged)
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir psycopg2-binary gunicorn sentry-sdk[flask]


# ── Stage 2: Runtime Image ────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Runtime-only system deps (libpq for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Create upload directory (persisted via volume in production)
RUN mkdir -p app/static/uploads/evidence \
    && chown -R appuser:appuser app/static/uploads

# Train ML classifier at build time (avoids cold-start latency)
RUN FLASK_APP=app FLASK_ENV=production python -c \
    "from app.ml.classifier import CrisisClassifier; CrisisClassifier.train(save=True)" \
    || echo "Warning: classifier training skipped (will fall back to keywords)"

USER appuser

# Expose port (Gunicorn will listen here)
EXPOSE 8000

# Health check for orchestrators (Kubernetes, ECS, etc.)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Production entrypoint: Gunicorn with threading mode (Render free tier compatible)
# Note: Flask-SocketIO falls back to long-polling on free tier (no sticky sessions)
CMD gunicorn \
    --worker-class=sync \
    --workers=1 \
    --threads=4 \
    --bind=0.0.0.0:${PORT:-8000} \
    --timeout=120 \
    --access-logfile=- \
    --error-logfile=- \
    run:app
