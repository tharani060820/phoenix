FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostgreSQL driver
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose default application port
EXPOSE 8000

ENV PORT=8000 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Health check to ensure service is live
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Start FastAPI production server via uvicorn (or python server.py fallback)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
