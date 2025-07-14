#!/usr/bin/env python3
"""
Test script for CodeVoice microservices
Run this after starting the Docker Compose services
"""

import requests
import json
import time

# Configuration
API_GATEWAY_URL = "http://localhost:8000"
SPEECH_SERVICE_URL = "http://localhost:8001"
CODE_SERVICE_URL = "http://localhost:8002"

def test_health_endpoints():
    """Test health endpoints of all services"""
    print("🏥 Testing health endpoints...")
    
    services = {
        "API Gateway": f"{API_GATEWAY_URL}/health",
        "Speech Service": f"{SPEECH_SERVICE_URL}/health",
        "Code Service": f"{CODE_SERVICE_URL}/health"
    }
    
    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name}: Healthy")
            else:
                print(f"❌ {service_name}: Unhealthy (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {service_name}: Error - {str(e)}")

def test_speech_service():
    """Test speech service with a mock audio request"""
    print("\n🎤 Testing speech service...")
    
    # Mock audio data (base64 encoded minimal audio)
    mock_audio = "UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT"
    
    try:
        response = requests.post(
            f"{API_GATEWAY_URL}/api/speech/transcribe",
            json={
                "audio_data": mock_audio,
                "audio_format": "webm",
                "language": "en"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Speech service: Working")
            print(f"   Transcript: {result.get('transcript', 'N/A')}")
        else:
            print(f"❌ Speech service: Error (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Speech service: Error - {str(e)}")

def test_code_service():
    """Test code generation service"""
    print("\n🤖 Testing code generation service...")
    
    try:
        response = requests.post(
            f"{API_GATEWAY_URL}/api/code/generate",
            json={
                "prompt": "Create a simple Python function that adds two numbers",
                "language": "python"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Code service: Working")
            print(f"   Generated code length: {len(result.get('code', ''))} characters")
            print(f"   Language: {result.get('language', 'N/A')}")
        else:
            print(f"❌ Code service: Error (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Code service: Error - {str(e)}")

def test_end_to_end():
    """Test the complete flow: speech -> code generation"""
    print("\n🔄 Testing end-to-end flow...")
    
    # Mock audio data
    mock_audio = "UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT"
    
    try:
        # Step 1: Transcribe audio
        print("   Step 1: Transcribing audio...")
        transcription_response = requests.post(
            f"{API_GATEWAY_URL}/api/speech/transcribe",
            json={
                "audio_data": mock_audio,
                "audio_format": "webm",
                "language": "en"
            },
            timeout=30
        )
        
        if transcription_response.status_code != 200:
            print(f"   ❌ Transcription failed: {transcription_response.status_code}")
            return
            
        transcription_result = transcription_response.json()
        transcript = transcription_result.get('transcript', '')
        print(f"   ✅ Transcription: {transcript}")
        
        # Step 2: Generate code from transcript
        if transcript and len(transcript) > 3:
            print("   Step 2: Generating code...")
            code_response = requests.post(
                f"{API_GATEWAY_URL}/api/code/generate",
                json={
                    "prompt": transcript,
                    "language": "python"
                },
                timeout=30
            )
            
            if code_response.status_code == 200:
                code_result = code_response.json()
                print(f"   ✅ Code generation: Success")
                print(f"   Code length: {len(code_result.get('code', ''))} characters")
            else:
                print(f"   ❌ Code generation failed: {code_response.status_code}")
        else:
            print("   ⚠️  Skipping code generation (no transcript)")
            
    except Exception as e:
        print(f"   ❌ End-to-end test failed: {str(e)}")

def test_api_gateway_routing():
    """Test API Gateway routing"""
    print("\n🌐 Testing API Gateway routing...")
    
    routes = [
        "/health",
        "/api/speech/languages",
        "/api/code/languages",
        "/metrics"
    ]
    
    for route in routes:
        try:
            response = requests.get(f"{API_GATEWAY_URL}{route}", timeout=5)
            if response.status_code in [200, 204]:
                print(f"✅ Route {route}: Working")
            else:
                print(f"❌ Route {route}: Error (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Route {route}: Error - {str(e)}")

def main():
    """Run all tests"""
    print("🚀 CodeVoice Microservices Test Suite")
    print("=" * 50)
    
    # Wait a moment for services to be ready
    print("⏳ Waiting for services to start...")
    time.sleep(5)
    
    # Run tests
    test_health_endpoints()
    test_api_gateway_routing()
    test_speech_service()
    test_code_service()
    test_end_to_end()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")

if __name__ == "__main__":
    main() 