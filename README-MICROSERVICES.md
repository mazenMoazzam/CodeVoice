# CodeVoice Microservices - Testing Guide

## 🚀 **What We've Built**

We've transformed your monolithic CodeVoice backend into a **microservices architecture** with:

### **Services Created:**
1. **API Gateway (Nginx)** - Routes requests to appropriate services
2. **Speech Service** - Handles audio transcription (extracted from your backend)
3. **Code Generation Service** - Generates code from prompts (extracted from your backend)
4. **Weather Service** - New service for weather data (partially created)

### **Key Features Added:**
- ✅ **Service Health Checks** - Each service has `/health` endpoints
- ✅ **Prometheus Metrics** - Monitoring and observability
- ✅ **Structured Logging** - Professional logging with structlog
- ✅ **Rate Limiting** - Nginx-based rate limiting
- ✅ **Service Discovery** - API Gateway routes requests appropriately
- ✅ **CORS Support** - Cross-origin requests handled
- ✅ **Load Balancing** - Ready for multiple service instances

## 🧪 **Testing the Microservices**

### **Step 1: Start the Services**
```bash
# Make sure you're in the CodeVoice directory
cd CodeVoice

# Start all services with Docker Compose
docker-compose up -d

# Check if services are running
docker-compose ps
```

### **Step 2: Test the Services**
```bash
# Run the test script
python test-microservices.py
```

### **Step 3: Test the Frontend**
```bash
# Start the frontend (in a new terminal)
cd frontend
npm run dev
```

Then visit `http://localhost:3000` and test the voice-to-code functionality.

## 🔍 **What the Test Script Checks**

1. **Health Endpoints** - Verifies all services are running
2. **API Gateway Routing** - Tests Nginx routing to services
3. **Speech Service** - Tests audio transcription
4. **Code Service** - Tests code generation
5. **End-to-End Flow** - Tests complete voice → code pipeline

## 🌐 **API Endpoints**

### **API Gateway (Nginx) - Port 8000**
- `GET /health` - Gateway health check
- `GET /metrics` - Prometheus metrics
- `POST /api/speech/transcribe` - Audio transcription
- `POST /api/code/generate` - Code generation
- `GET /api/speech/languages` - Supported languages
- `GET /api/code/languages` - Supported programming languages

### **Speech Service - Port 8001**
- `GET /health` - Service health
- `POST /transcribe` - Audio transcription
- `GET /languages` - Supported languages

### **Code Service - Port 8002**
- `GET /health` - Service health
- `POST /generate` - Code generation
- `GET /languages` - Supported languages

## 🔧 **Troubleshooting**

### **Services Not Starting**
```bash
# Check logs
docker-compose logs api-gateway
docker-compose logs speech-service
docker-compose logs code-service

# Restart services
docker-compose restart
```

### **Frontend Can't Connect**
- Make sure the API Gateway is running on port 8000
- Check that the frontend is making requests to `http://localhost:8000`
- Verify CORS settings in the Nginx configuration

### **Audio Transcription Issues**
- Ensure ffmpeg is installed in the speech service container
- Check that the audio format is supported (webm, wav, mp3)
- Verify the OpenAI API key is set in the code service

## 📊 **Monitoring**

### **Prometheus Metrics**
- Visit `http://localhost:9090` for Prometheus
- Visit `http://localhost:3001` for Grafana (admin/admin)

### **Service Logs**
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f speech-service
docker-compose logs -f code-service
```

## 🎯 **Next Steps**

Once this basic setup is working, we can add:

1. **Weather Service** - Complete the weather microservice
2. **User Service** - Authentication and user management
3. **Task Service** - Calendar integration
4. **Notification Service** - Real-time notifications
5. **Kubernetes Deployment** - Production orchestration
6. **gRPC Communication** - Inter-service communication
7. **Advanced Monitoring** - Distributed tracing

## 🏆 **FAANG Interview Highlights**

This microservices architecture demonstrates:

- **System Design** - Microservices, service communication, load balancing
- **Scalability** - Horizontal scaling, service isolation
- **Reliability** - Health checks, graceful degradation
- **Observability** - Metrics, logging, monitoring
- **DevOps** - Containerization, orchestration
- **Performance** - Caching, rate limiting, compression

---

**Ready to test? Run `docker-compose up -d` and then `python test-microservices.py`!** 