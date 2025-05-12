# Use official Python 3.10.9 image
FROM python:3.10.9-slim

# Install Git and other essentials (e.g., build tools)
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Default command (customize as needed)
CMD ["bash"]