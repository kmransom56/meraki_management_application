# Use Python 3.11 slim image for smaller size and better performance
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_LINK_MODE=copy

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
RUN mkdir -p /app/logs /app/data /app/config /app/static /app/templates

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash merakiuser && \
    chown -R merakiuser:merakiuser /app
USER merakiuser

# Expose port for web interface
EXPOSE 5000

# Health check using Python instead of curl for better reliability
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health', timeout=10)" || exit 1

# Start the application
CMD ["python", "docker_wrapper.py"]