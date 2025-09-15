# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# We run as root here, so no sudo is needed.
# --no-install-recommends keeps the image size smaller.
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libgthread-2.0-0 \
    libsm6 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Find the tesseract executable path and set it as an environment variable
# This makes the setup resilient to changes in package installation paths.
ENV TESSERACT_CMD_PATH=/usr/bin/tesseract

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

CMD ["gunicorn", "app:app"]