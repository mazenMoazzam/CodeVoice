#!/usr/bin/env python3
"""
Simple test script for CodeVoice microservices
This tests the services individually without Docker
"""

import requests
import json
import time
import os

def test_speech_service_direct():
    """Test speech service directly (if running)"""
    print("🎤 Testing Speech Service directly...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Speech Service is running on port 8001")
            return True
        else:
            print(f"❌ Speech Service health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Speech Service not running on port 8001")
        return False
    except Exception as e:
        print(f"❌ Error testing Speech Service: {str(e)}")
        return False

def test_code_service_direct():
    """Test code service directly (if running)"""
    print("🤖 Testing Code Service directly...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Code Service is running on port 8002")
            return True
        else:
            print(f"❌ Code Service health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Code Service not running on port 8002")
        return False
    except Exception as e:
        print(f"❌ Error testing Code Service: {str(e)}")
        return False

def test_api_gateway():
    """Test API Gateway (if running)"""
    print("🌐 Testing API Gateway...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Gateway is running on port 8000")
            return True
        else:
            print(f"❌ API Gateway health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API Gateway not running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error testing API Gateway: {str(e)}")
        return False

def test_code_generation():
    """Test code generation with a simple prompt"""
    print("🤖 Testing Code Generation...")
    
    # Check if OpenAI API key is available
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️  OPENAI_API_KEY not set. Skipping code generation test.")
        return False
    
    try:
        # Test with API Gateway
        response = requests.post(
            "http://localhost:8000/api/code/generate",
            json={
                "prompt": "Create a simple Python function that adds two numbers",
                "language": "python"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Code generation via API Gateway: Success")
            print(f"   Code length: {len(result.get('code', ''))} characters")
            return True
        else:
            print(f"❌ Code generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API Gateway")
        return False
    except Exception as e:
        print(f"❌ Error testing code generation: {str(e)}")
        return False

def test_frontend_integration():
    """Test if frontend can connect to backend"""
    print("🎨 Testing Frontend Integration...")
    
    try:
        # Test the frontend API route
        response = requests.post(
            "http://localhost:3000/api/transcribe",
            json={
                "audio": "dGVzdA==",  # base64 encoded "test"
                "language": "python"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Frontend API route is working")
            return True
        else:
            print(f"❌ Frontend API route failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Frontend not running on port 3000")
        return False
    except Exception as e:
        print(f"❌ Error testing frontend: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 CodeVoice Simple Test Suite")
    print("=" * 50)
    
    # Test individual services
    speech_ok = test_speech_service_direct()
    code_ok = test_code_service_direct()
    gateway_ok = test_api_gateway()
    
    # Test integrations
    if gateway_ok:
        code_gen_ok = test_code_generation()
    else:
        code_gen_ok = False
    
    frontend_ok = test_frontend_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Speech Service: {'✅' if speech_ok else '❌'}")
    print(f"   Code Service: {'✅' if code_ok else '❌'}")
    print(f"   API Gateway: {'✅' if gateway_ok else '❌'}")
    print(f"   Code Generation: {'✅' if code_gen_ok else '❌'}")
    print(f"   Frontend Integration: {'✅' if frontend_ok else '❌'}")
    
    if not any([speech_ok, code_ok, gateway_ok]):
        print("\n💡 Next Steps:")
        print("   1. Start Docker Desktop")
        print("   2. Run: docker-compose -f docker-compose-simple.yml up -d")
        print("   3. Or start services individually:")
        print("      - cd services/speech-service && python main.py")
        print("      - cd services/code-service && python main.py")

if __name__ == "__main__":
    main() 