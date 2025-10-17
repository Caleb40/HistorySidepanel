FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies (Alpine uses apk)
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    curl

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser -D -u 1000 backend && \
    chown -R backend:backend /app
USER backend

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Start application - FIXED: Use src.main instead of main
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]