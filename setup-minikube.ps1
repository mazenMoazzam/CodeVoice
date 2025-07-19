# CodeVoice Minikube Setup Script
Write-Host "🚀 Setting up Minikube for CodeVoice..." -ForegroundColor Green

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Please run this script as Administrator" -ForegroundColor Red
    exit 1
}

# Install Chocolatey if not present
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    refreshenv
}

# Install required tools
Write-Host "🔧 Installing required tools..." -ForegroundColor Yellow

# Install Minikube
if (!(Get-Command minikube -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Minikube..." -ForegroundColor Yellow
    choco install minikube -y
    refreshenv
}

# Install kubectl
if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing kubectl..." -ForegroundColor Yellow
    choco install kubernetes-cli -y
    refreshenv
}

# Install Docker Desktop (if not present)
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Docker Desktop..." -ForegroundColor Yellow
    choco install docker-desktop -y
    Write-Host "⚠️  Please start Docker Desktop manually and restart your terminal" -ForegroundColor Yellow
}

# Start Minikube
Write-Host "🚀 Starting Minikube..." -ForegroundColor Green
minikube start --driver=docker --memory=4096 --cpus=2

# Enable addons
Write-Host "🔧 Enabling Minikube addons..." -ForegroundColor Yellow
minikube addons enable ingress
minikube addons enable metrics-server

# Show status
Write-Host "✅ Minikube setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Status:" -ForegroundColor Cyan
minikube status
Write-Host ""
Write-Host "🌐 Dashboard:" -ForegroundColor Cyan
Write-Host "Run: minikube dashboard" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Next steps:" -ForegroundColor Cyan
Write-Host "1. Build Docker images: docker build -t codevoice/api-gateway ./services/api-gateway" -ForegroundColor White
Write-Host "2. Load images to Minikube: minikube image load codevoice/api-gateway" -ForegroundColor White
Write-Host "3. Deploy to K8s: kubectl apply -f k8s/" -ForegroundColor White 