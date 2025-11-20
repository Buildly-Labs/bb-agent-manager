# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Copy requirements and install minimal dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir mcp httpx

# Copy MCP server
COPY buildly_mcp_server.py .

# Create necessary directories
RUN mkdir -p /app/devdocs

# Default command - run MCP server on stdio
CMD ["python3", "buildly_mcp_server.py"]

