# Use Python 3.11 slim image for smaller size and better performance
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies needed for your application
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libsqlcipher-dev \
    libsqlite3-dev \
    sqlite3 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

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

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start the application
CMD ["python", "docker_wrapper.py"]