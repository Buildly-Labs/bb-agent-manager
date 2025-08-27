# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# Copy the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/devdocs

# Make test scripts executable
RUN chmod +x test_server.py test_client.py

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["uvicorn", "test_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
