# Use Python 3.11 slim image for smaller size and better performance
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_LINK_MODE=copy \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libsqlcipher-dev \
    libsqlite3-dev \
    sqlite3 \
    curl \
    git \
    ca-certificates \
    openssh-client \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv - much faster than pip
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies with uv (much faster than pip)
RUN uv pip install -r requirements.txt --system --native-tls --trusted-host pypi.org --trusted-host files.pythonhosted.org

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/config /app/static /app/templates /app/modules /app/modules/fortigate

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash merakiuser && \
    chown -R merakiuser:merakiuser /app
USER merakiuser

# Expose port for web interface
EXPOSE 5000

# Health check for web application
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000', timeout=10)" || exit 1

# Start the enhanced web application with FortiManager integration
CMD ["python", "app.py"]