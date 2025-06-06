# Use official Python 3.10 slim image
FROM python:3.10-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies required for tkinter and pymongo
RUN apt-get update && \
    apt-get install -y \
    python3-tk \
    tk-dev \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure pymongo is available (optional safety)
RUN pip install pymongo

# Copy your application code
COPY . .

# Default command (adjust as needed)
CMD ["python", "Call.py"]
