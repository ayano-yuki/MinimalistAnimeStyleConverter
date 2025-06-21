FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create directories for models and input/output
RUN mkdir -p models input output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TORCH_HOME=/app/models
ENV HF_HOME=/app/models

# Expose volume for input/output
VOLUME ["/app/input", "/app/output", "/app/models"]

# Default command
CMD ["python", "main.py", "--help"]
