FROM python:3.12-slim

# System deps for Playwright and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Playwright browsers
RUN pip install --no-cache-dir playwright
RUN playwright install-deps chromium

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

ENV XANDER_ENV=production
ENV XANDER_PORT=8080

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "gateway.py"]
