FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies (FAISS often needs build-essential for some builds, though we use faiss-cpu)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose API port for Hugging Face Spaces (7860 is default)
EXPOSE 7860

# Run ingest script to build ephemeral Qdrant DB at runtime, then start FastAPI
CMD python ingest.py && uvicorn main:app --host 0.0.0.0 --port 7860
