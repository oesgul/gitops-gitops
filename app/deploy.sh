#!/bin/bash

# Deployment script for the image recognition application

set -e

echo "Deploying Image Recognition Application..."

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -k k8s/

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/image-recognition-app -n image-recognition

# Check pod status
echo "Checking pod status..."
kubectl get pods -n image-recognition -l app=image-recognition-app

# Get service information
echo "Service information:"
kubectl get svc -n image-recognition

# Get route information (OpenShift)
echo "Route information:"
kubectl get route -n image-recognition || echo "Routes not available (not on OpenShift)"

echo "Deployment completed successfully!"

# Optional: Run integration tests
# echo "Running integration tests..."
# python -m pytest tests/test_integration.py -v