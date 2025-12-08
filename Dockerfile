# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies to a virtual environment
COPY requirements-docker.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements-docker.txt

# Stage 2: Runtime (using distroless Python)
FROM gcr.io/distroless/python3-debian12

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app ./app
COPY config ./config
COPY data ./data
COPY dashboards ./dashboards

# Create necessary directories (distroless doesn't have mkdir, so we copy empty dirs)
COPY --from=builder /tmp /app/trulens_data

# Set Python path
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages:/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the application (distroless uses array format)
ENTRYPOINT ["python3", "-m", "uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0", "--port", "8000"]
