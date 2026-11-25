# Nebulyx Autonomous Instagram Reel Lead Intelligence & Sellbird CRM
# Production Dockerfile
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    HOST=0.0.0.0 \
    PORT=8088

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries
RUN playwright install chromium

# Copy application source
COPY lead_scraper/ ./lead_scraper/

# Expose HTTP REST API and Dashboard port
EXPOSE 8088

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8088/api/status || exit 1

# Default command: launch the Nebulyx Lead Intelligence Server
CMD ["python", "lead_scraper/server.py"]
