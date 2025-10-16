# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps required to build some Python packages (if needed)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy application code
COPY . .

# Default port (common for uvicorn/fastapi)
EXPOSE 8000

# Default command: explicitly run the Python main script
# This ensures the container starts the bundled `main.py` Hello World server.
CMD ["python", "main.py"]
