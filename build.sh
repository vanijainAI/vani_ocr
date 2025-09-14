#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies for Tesseract and Poppler
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils

# Upgrade pip and install Python dependencies into the virtual environment
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt