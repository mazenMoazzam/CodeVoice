# 🚀 CodeVoice Microservices - Quick Start

## **Option 1: Test with Docker (Recommended)**

### **Step 1: Start Docker Desktop**
1. Open Docker Desktop application
2. Wait for it to fully start (green icon in system tray)

### **Step 2: Start Services**
```bash
# Navigate to CodeVoice directory
cd CodeVoice

# Start simplified services
docker-compose -f docker-compose-simple.yml up -d

# Check if services are running
docker-compose -f docker-compose-simple.yml ps
```

### **Step 3: Test Services**
```bash
# Run the test script
python test-simple.py
```

### **Step 4: Test Frontend**
```bash
# In a new terminal, start the frontend
cd frontend
npm run dev
```

Then visit `http://localhost:3000` and test voice-to-code!

---

## **Option 2: Test Services Individually (No Docker)**

### **Step 1: Set up Environment**
```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### **Step 2: Start Speech Service**
```bash
cd services/speech-service
pip install -r requirements.txt
python main.py
```

### **Step 3: Start Code Service**
```bash
# In a new terminal
cd services/code-service
pip install -r requirements.txt
python main.py
```

### **Step 4: Test**
```bash
# In another terminal
python test-simple.py
```

---

## **🔧 Troubleshooting**

### **Docker Issues:**
- Make sure Docker Desktop is running
- Try restarting Docker Desktop
- Check if ports 8000, 8001, 8002 are available

### **API Key Issues:**
- Set your OpenAI API key: `export OPENAI_API_KEY=your_key_here`
- Or create a `.env` file in the CodeVoice directory

### **Port Conflicts:**
- If ports are in use, stop other services
- Or modify the docker-compose file to use different ports

### **Service Not Starting:**
```bash
# Check logs
docker-compose -f docker-compose-simple.yml logs

# Restart services
docker-compose -f docker-compose-simple.yml restart
```

---

## **✅ What Should Work**

After starting the services, you should see:
- ✅ API Gateway on `http://localhost:8000/health`
- ✅ Speech Service on `http://localhost:8001/health`
- ✅ Code Service on `http://localhost:8002/health`
- ✅ Frontend on `http://localhost:3000`

---

## **🎯 Quick Test Commands**

```bash
# Test API Gateway
curl http://localhost:8000/health

# Test Speech Service
curl http://localhost:8001/health

# Test Code Service
curl http://localhost:8002/health

# Test Code Generation
curl -X POST http://localhost:8000/api/code/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"print hello world","language":"python"}'
```

**Ready to test? Choose Option 1 or 2 above!** 