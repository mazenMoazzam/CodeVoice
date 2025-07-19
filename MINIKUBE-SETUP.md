# 🚀 CodeVoice Minikube Setup Guide

## Prerequisites

### 1. Install Required Tools

#### Option A: Using Chocolatey (Recommended)
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install tools
choco install minikube -y
choco install kubernetes-cli -y
choco install docker-desktop -y
```

#### Option B: Manual Installation
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 2. Start Docker Desktop
Make sure Docker Desktop is running before proceeding.

## Quick Setup

### 1. Run the Setup Script
```powershell
# Run as Administrator
.\setup-minikube.ps1
```

### 2. Deploy CodeVoice
```powershell
# Deploy to Minikube
.\deploy-minikube.ps1
```

## Manual Setup

### 1. Start Minikube
```powershell
minikube start --driver=docker --memory=4096 --cpus=2
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Create Namespace and Config
```powershell
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
```

### 3. Build and Load Images
```powershell
# Build images
docker build -t codevoice/api-gateway:latest ./services/api-gateway
docker build -t codevoice/speech-service:latest ./services/speech-service
docker build -t codevoice/code-service:latest ./services/code-service
docker build -t codevoice/live-ai-coding-service:latest ./services/live-ai-coding-service
docker build -t codevoice/collaborative-docs-service:latest ./services/collaborative-docs-service
docker build -t codevoice/frontend:latest ./frontend

# Load to Minikube
minikube image load codevoice/api-gateway:latest
minikube image load codevoice/speech-service:latest
minikube image load codevoice/code-service:latest
minikube image load codevoice/live-ai-coding-service:latest
minikube image load codevoice/collaborative-docs-service:latest
minikube image load codevoice/frontend:latest
```

### 4. Deploy Services
```powershell
kubectl apply -f k8s/api-gateway-deployment.yaml
kubectl apply -f k8s/speech-service-deployment.yaml
kubectl apply -f k8s/code-service-deployment.yaml
kubectl apply -f k8s/live-ai-coding-deployment.yaml
kubectl apply -f k8s/collaborative-docs-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

## Access Your Application

### 1. Get Service URLs
```powershell
# Frontend
minikube service frontend-service -n codevoice --url

# API Gateway
minikube service api-gateway-service -n codevoice --url
```

### 2. Open Dashboard
```powershell
minikube dashboard
```

## Troubleshooting

### Check Pod Status
```powershell
kubectl get pods -n codevoice
kubectl describe pod <pod-name> -n codevoice
```

### Check Logs
```powershell
kubectl logs -f deployment/api-gateway -n codevoice
kubectl logs -f deployment/frontend -n codevoice
```

### Restart Services
```powershell
kubectl rollout restart deployment/api-gateway -n codevoice
kubectl rollout restart deployment/frontend -n codevoice
```

### Clean Up
```powershell
# Delete all resources
kubectl delete namespace codevoice

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Next Steps

1. **Test the application** - Open the frontend URL in your browser
2. **Try voice commands** - Test the Live AI Coding feature
3. **Test collaboration** - Open multiple browser tabs for real-time editing
4. **Deploy to EKS** - When ready, deploy to AWS EKS for production

## Configuration

### Update API Keys
Edit `k8s/secrets.yaml` and update the base64-encoded API keys:
```powershell
# Encode your API keys
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("your-openai-api-key"))
```

### Scale Services
```powershell
# Scale API Gateway to 3 replicas
kubectl scale deployment api-gateway --replicas=3 -n codevoice
```

## Monitoring

### View Resource Usage
```powershell
# Resource usage
kubectl top pods -n codevoice
kubectl top nodes

# Service endpoints
kubectl get endpoints -n codevoice
```

### Health Checks
```powershell
# Check service health
kubectl get pods -n codevoice -o wide
kubectl describe service api-gateway-service -n codevoice
``` 