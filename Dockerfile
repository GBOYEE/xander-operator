FROM python:3.10-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and its browser dependencies
RUN pip install --no-cache-dir playwright
RUN playwright install-deps chromium

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Install the package itself
RUN pip install -e .

# Default command
CMD ["python", "-m", "operator.cli"]
