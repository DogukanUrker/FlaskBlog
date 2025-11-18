# FlaskBlog Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY app/pyproject.toml app/uv.lock* ./

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml


# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash flaskblog && \
    mkdir -p /app/db /app/log && \
    chown -R flaskblog:flaskblog /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=flaskblog:flaskblog app/ .

# Create necessary directories with correct permissions
RUN mkdir -p db log translations static templates routes utils && \
    chown -R flaskblog:flaskblog /app && \
    chmod -R 755 /app && \
    chmod 750 db log

# Switch to non-root user
USER flaskblog

# Expose port
EXPOSE 1283

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import socket; sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); sock.settimeout(2); result = sock.connect_ex(('localhost', 1283)); sock.close(); exit(result)"

# Volume for persistent data
VOLUME ["/app/db", "/app/log"]

# Default command
CMD ["python3", "app.py"]
