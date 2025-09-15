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

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Find the tesseract executable path and write it to an environment file.
# This makes the setup resilient to changes in package installation paths.
RUN echo "export TESSERACT_CMD=$(which tesseract)" > /app/tesseract_env.sh

# Copy the rest of the application code into the container
COPY . .

# The CMD instruction sources the environment file and then starts Gunicorn.
CMD . /app/tesseract_env.sh && gunicorn --bind 0.0.0.0:$PORT --worker-tmp-dir /dev/shm app:app