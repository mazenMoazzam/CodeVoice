#!/bin/bash

# CodeVoice Minikube Deployment Script
echo "🚀 Deploying CodeVoice to Minikube..."

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo "❌ Minikube is not running. Starting Minikube..."
    minikube start --driver=docker --memory=4096 --cpus=2
fi

# Enable addons
echo "🔧 Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f namespace.yaml

# Create ConfigMap and Secrets
echo "🔐 Creating ConfigMap and Secrets..."
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml

# Build and load Docker images
echo "🐳 Building Docker images..."

# API Gateway
echo "Building API Gateway..."
docker build -t codevoice/api-gateway:latest ./services/api-gateway
minikube image load codevoice/api-gateway:latest

# Speech Service
echo "Building Speech Service..."
docker build -t codevoice/speech-service:latest ./services/speech-service
minikube image load codevoice/speech-service:latest

# Code Service
echo "Building Code Service..."
docker build -t codevoice/code-service:latest ./services/code-service
minikube image load codevoice/code-service:latest

# Live AI Coding Service
echo "Building Live AI Coding Service..."
docker build -t codevoice/live-ai-coding-service:latest ./services/live-ai-coding-service
minikube image load codevoice/live-ai-coding-service:latest

# Collaborative Docs Service
echo "Building Collaborative Docs Service..."
docker build -t codevoice/collaborative-docs-service:latest ./services/collaborative-docs-service
minikube image load codevoice/collaborative-docs-service:latest

# Frontend
echo "Building Frontend..."
docker build -t codevoice/frontend:latest ./frontend
minikube image load codevoice/frontend:latest

# Deploy services
echo "🚀 Deploying services..."

# Deploy API Gateway
kubectl apply -f api-gateway-deployment.yaml

# Deploy other services (simplified for testing)
kubectl apply -f speech-service-deployment.yaml
kubectl apply -f code-service-deployment.yaml
kubectl apply -f live-ai-coding-deployment.yaml
kubectl apply -f collaborative-docs-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/api-gateway -n codevoice
kubectl wait --for=condition=available --timeout=300s deployment/speech-service -n codevoice
kubectl wait --for=condition=available --timeout=300s deployment/code-service -n codevoice
kubectl wait --for=condition=available --timeout=300s deployment/live-ai-coding-service -n codevoice
kubectl wait --for=condition=available --timeout=300s deployment/collaborative-docs-service -n codevoice
kubectl wait --for=condition=available --timeout=300s deployment/frontend -n codevoice

# Show status
echo "✅ Deployment complete!"
echo ""
echo "📊 Pod status:"
kubectl get pods -n codevoice
echo ""
echo "🌐 Services:"
kubectl get services -n codevoice
echo ""
echo "🔗 Access URLs:"
echo "Frontend: $(minikube service frontend-service -n codevoice --url)"
echo "API Gateway: $(minikube service api-gateway-service -n codevoice --url)"
echo ""
echo "📈 Dashboard:"
echo "Run: minikube dashboard"
echo ""
echo "🔍 Debug commands:"
echo "kubectl logs -f deployment/api-gateway -n codevoice"
echo "kubectl describe pod -l app=api-gateway -n codevoice" 