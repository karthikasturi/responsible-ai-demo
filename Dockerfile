# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies in a single layer and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy only requirements first for better layer caching
COPY requirements-docker.txt .

# Install Python dependencies to a separate location
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefix=/install -r requirements-docker.txt && \
    find /install -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true && \
    find /install -type f -name '*.pyc' -delete 2>/dev/null || true && \
    find /install -type f -name '*.pyo' -delete 2>/dev/null || true

# Stage 2: Runtime (using slim Python for better compatibility)
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python dependencies from builder
COPY --from=builder /install /usr/local

# Copy only necessary application code
COPY app ./app
COPY config ./config

# Create necessary directories
RUN mkdir -p /app/data /app/trulens_data /app/dashboards

# Set Python path and environment
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages:/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
