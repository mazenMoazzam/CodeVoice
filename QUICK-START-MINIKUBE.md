# 🚀 Quick Start: CodeVoice on Minikube

## Prerequisites Installation

### 1. Install Docker Desktop
Download and install from: https://www.docker.com/products/docker-desktop/

### 2. Install Minikube
Download from: https://minikube.sigs.k8s.io/docs/start/
- Download the Windows installer
- Run as Administrator
- Add to PATH

### 3. Install kubectl
Download from: https://kubernetes.io/docs/tasks/tools/
- Download the Windows binary
- Add to PATH

## Quick Deployment

### 1. Start Minikube
```powershell
# Start Minikube with Docker driver
minikube start --driver=docker --memory=4096 --cpus=2

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Deploy CodeVoice
```powershell
# Create namespace and config
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Build Docker images
docker build -t codevoice/api-gateway:latest ./services/api-gateway
docker build -t codevoice/speech-service:latest ./services/speech-service
docker build -t codevoice/code-service:latest ./services/code-service
docker build -t codevoice/live-ai-coding-service:latest ./services/live-ai-coding-service
docker build -t codevoice/collaborative-docs-service:latest ./services/collaborative-docs-service
docker build -t codevoice/frontend:latest ./frontend

# Load images to Minikube
minikube image load codevoice/api-gateway:latest
minikube image load codevoice/speech-service:latest
minikube image load codevoice/code-service:latest
minikube image load codevoice/live-ai-coding-service:latest
minikube image load codevoice/collaborative-docs-service:latest
minikube image load codevoice/frontend:latest

# Deploy services
kubectl apply -f k8s/api-gateway-deployment.yaml
kubectl apply -f k8s/speech-service-deployment.yaml
kubectl apply -f k8s/code-service-deployment.yaml
kubectl apply -f k8s/live-ai-coding-deployment.yaml
kubectl apply -f k8s/collaborative-docs-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### 3. Access Your Application
```powershell
# Get service URLs
minikube service frontend-service -n codevoice --url
minikube service api-gateway-service -n codevoice --url

# Open dashboard
minikube dashboard
```

## Troubleshooting

### Check Status
```powershell
# Pod status
kubectl get pods -n codevoice

# Service status
kubectl get services -n codevoice

# Minikube status
minikube status
```

### View Logs
```powershell
# API Gateway logs
kubectl logs -f deployment/api-gateway -n codevoice

# Frontend logs
kubectl logs -f deployment/frontend -n codevoice
```

### Restart Services
```powershell
# Restart deployments
kubectl rollout restart deployment/api-gateway -n codevoice
kubectl rollout restart deployment/frontend -n codevoice
```

## Clean Up
```powershell
# Delete all resources
kubectl delete namespace codevoice

# Stop Minikube
minikube stop

# Delete cluster
minikube delete
```

## Next Steps
1. Test the application in your browser
2. Try voice commands and real-time collaboration
3. When ready, deploy to AWS EKS for production 