#!/bin/bash

# Build script for the image recognition application

set -e

echo "Building Image Recognition Application..."

# Build Docker image
echo "Building Docker image..."
docker build -t image-recognition-app:latest .

# Run tests
echo "Running tests..."
python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

echo "Build completed successfully!"

# Optional: Push to registry (uncomment if needed)
# echo "Pushing to registry..."
# docker tag image-recognition-app:latest your-registry/image-recognition-app:latest
# docker push your-registry/image-recognition-app:latest