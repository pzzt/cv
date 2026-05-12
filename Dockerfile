# =============================================================================
# Multi-stage Dockerfile for CV API
# =============================================================================
# This Dockerfile uses a multi-stage build to:
# 1. Keep the final image small by excluding build dependencies
# 2. Ensure reproducible builds with specific versions
# 3. Run as non-root user for security
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder
# Installs build dependencies and creates a virtual environment
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

# Set build-time environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for building
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements/ requirements/
RUN pip install --upgrade pip && \
    pip install -r requirements/prod.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime
# Creates the minimal production image
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Set runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    CV_API_APP_ENVIRONMENT="production"

# Create non-root user for security
RUN groupadd -r cvuser && \
    useradd -r -g cvuser -u 1000 cvuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set up application directory
WORKDIR /app

# Copy application code
COPY --chown=cvuser:cvuser app/ ./app/

# Copy static frontend files
COPY --chown=cvuser:cvuser static/ ./static/

# Create data directory and copy data files
RUN mkdir -p /app/data && \
    chown -R cvuser:cvuser /app/data
COPY --chown=cvuser:cvuser data/ ./data/

# Switch to non-root user
USER cvuser

# Expose port (for documentation purposes - actual port is configurable)
EXPOSE 8000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Run the application with gunicorn
# Uses uvicorn workers for async support
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "--timeout", "30", \
     "--graceful-timeout", "10", \
     "app.main:app"]
