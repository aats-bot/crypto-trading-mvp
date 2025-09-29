# Dockerfile otimizado - Estrutura SRC exclusivamente
# Remove dependência da pasta app/ obsoleta

FROM crypto-trading-mvp-api:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy source code (src/ apenas)
COPY src/ /app/src/

# Install additional dependencies
RUN pip install --no-cache-dir PyJWT==2.8.0 python-multipart==0.0.6 || true

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Set working directory
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Command to run the application (src/ structure)
CMD ["python", "src/api/main.py"]
