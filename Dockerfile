FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash appuser \
 && chown -R appuser:appuser /app

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

ENV XANDER_OPERATOR_ENV=production
ENV XANDER_OPERATOR_PORT=8001

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

USER appuser

CMD ["uvicorn", "xander_operator.api.server:app", "--host", "0.0.0.0", "--port", "8001"]
