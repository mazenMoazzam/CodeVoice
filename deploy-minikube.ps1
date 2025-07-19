# CodeVoice Minikube Deployment Script
Write-Host "🚀 Deploying CodeVoice to Minikube..." -ForegroundColor Green

# Check if Minikube is running
$minikubeStatus = minikube status --format=json | ConvertFrom-Json
if ($minikubeStatus.Host -ne "Running") {
    Write-Host "❌ Minikube is not running. Starting Minikube..." -ForegroundColor Yellow
    minikube start --driver=docker --memory=4096 --cpus=2
}

# Enable addons
Write-Host "🔧 Enabling Minikube addons..." -ForegroundColor Yellow
minikube addons enable ingress
minikube addons enable metrics-server

# Create namespace
Write-Host "📦 Creating namespace..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml

# Create ConfigMap and Secrets
Write-Host "🔐 Creating ConfigMap and Secrets..." -ForegroundColor Yellow
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Build and load Docker images
Write-Host "🐳 Building Docker images..." -ForegroundColor Yellow

# API Gateway
Write-Host "Building API Gateway..." -ForegroundColor Cyan
docker build -t codevoice/api-gateway:latest ./services/api-gateway
minikube image load codevoice/api-gateway:latest

# Speech Service
Write-Host "Building Speech Service..." -ForegroundColor Cyan
docker build -t codevoice/speech-service:latest ./services/speech-service
minikube image load codevoice/speech-service:latest

# Code Service
Write-Host "Building Code Service..." -ForegroundColor Cyan
docker build -t codevoice/code-service:latest ./services/code-service
minikube image load codevoice/code-service:latest

# Live AI Coding Service
Write-Host "Building Live AI Coding Service..." -ForegroundColor Cyan
docker build -t codevoice/live-ai-coding-service:latest ./services/live-ai-coding-service
minikube image load codevoice/live-ai-coding-service:latest

# Collaborative Docs Service
Write-Host "Building Collaborative Docs Service..." -ForegroundColor Cyan
docker build -t codevoice/collaborative-docs-service:latest ./services/collaborative-docs-service
minikube image load codevoice/collaborative-docs-service:latest

# Frontend
Write-Host "Building Frontend..." -ForegroundColor Cyan
docker build -t codevoice/frontend:latest ./frontend
minikube image load codevoice/frontend:latest

# Deploy services
Write-Host "🚀 Deploying services..." -ForegroundColor Yellow

# Deploy all services
kubectl apply -f k8s/api-gateway-deployment.yaml
kubectl apply -f k8s/speech-service-deployment.yaml
kubectl apply -f k8s/code-service-deployment.yaml
kubectl apply -f k8s/live-ai-coding-deployment.yaml
kubectl apply -f k8s/collaborative-docs-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Wait for deployments
Write-Host "⏳ Waiting for deployments to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=available --timeout=300s deployment/api-gateway -n codevoice
kubectl wait --for=condition=available --timeout=300s deployment/speech-service -n codevoice
kubectl wait --for=condition=available --timeout=300s deployment/code-service -n codevoice
kubectl wait --for=condition=available --timeout=300s deployment/live-ai-coding-service -n codevoice
kubectl wait --for=condition=available --timeout=300s deployment/collaborative-docs-service -n codevoice
kubectl wait --for=condition=available --timeout=300s deployment/frontend -n codevoice

# Show status
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Pod status:" -ForegroundColor Cyan
kubectl get pods -n codevoice
Write-Host ""
Write-Host "🌐 Services:" -ForegroundColor Cyan
kubectl get services -n codevoice
Write-Host ""
Write-Host "🔗 Access URLs:" -ForegroundColor Cyan
$frontendUrl = minikube service frontend-service -n codevoice --url
Write-Host "Frontend: $frontendUrl" -ForegroundColor White
$apiUrl = minikube service api-gateway-service -n codevoice --url
Write-Host "API Gateway: $apiUrl" -ForegroundColor White
Write-Host ""
Write-Host "📈 Dashboard:" -ForegroundColor Cyan
Write-Host "Run: minikube dashboard" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Debug commands:" -ForegroundColor Cyan
Write-Host "kubectl logs -f deployment/api-gateway -n codevoice" -ForegroundColor White
Write-Host "kubectl describe pod -l app=api-gateway -n codevoice" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Your CodeVoice platform is now running on Minikube!" -ForegroundColor Green 