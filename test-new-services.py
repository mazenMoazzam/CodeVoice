#!/usr/bin/env python3
"""
Test script for the new Live AI Coding and Collaborative Documents services
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Service URLs
BASE_URL = "http://localhost:8000"
LIVE_CODING_URL = "http://localhost:8005"
COLLAB_DOCS_URL = "http://localhost:8006"

async def test_api_gateway_health():
    """Test API Gateway health check"""
    print("🔍 Testing API Gateway health...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ API Gateway is healthy")
                    print(f"   Services: {list(data.get('services', {}).keys())}")
                    return True
                else:
                    print(f"❌ API Gateway health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ API Gateway connection error: {e}")
            return False

async def test_live_ai_coding():
    """Test Live AI Coding service"""
    print("\n🤖 Testing Live AI Coding service...")
    async with aiohttp.ClientSession() as session:
        try:
            # Test code generation
            payload = {
                "voice_command": "Create a React todo component",
                "language": "javascript",
                "user_id": "test-user"
            }
            
            async with session.post(f"{BASE_URL}/api/live-coding/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Live AI Coding code generation works")
                    print(f"   Generated code length: {len(data.get('code', ''))} characters")
                    print(f"   Language: {data.get('language')}")
                    return True
                else:
                    print(f"❌ Live AI Coding failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Live AI Coding error: {e}")
            return False

async def test_collaborative_docs():
    """Test Collaborative Documents service"""
    print("\n📝 Testing Collaborative Documents service...")
    async with aiohttp.ClientSession() as session:
        try:
            # Test document creation
            params = {
                "title": "Test Document",
                "language": "javascript",
                "user_id": "test-user",
                "username": "TestUser"
            }
            
            async with session.post(f"{BASE_URL}/api/documents/create", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    doc_id = data.get('document', {}).get('id')
                    print("✅ Document creation works")
                    print(f"   Document ID: {doc_id}")
                    
                    # Test getting document
                    async with session.get(f"{BASE_URL}/api/documents/{doc_id}") as get_response:
                        if get_response.status == 200:
                            print("✅ Document retrieval works")
                            return True
                        else:
                            print(f"❌ Document retrieval failed: {get_response.status}")
                            return False
                else:
                    print(f"❌ Document creation failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Collaborative Documents error: {e}")
            return False

async def test_voice_transcription():
    """Test voice transcription service"""
    print("\n🎤 Testing Voice Transcription service...")
    async with aiohttp.ClientSession() as session:
        try:
            # Test with dummy audio data
            payload = {
                "audio": "dummy_base64_audio_data",
                "language": "en"
            }
            
            async with session.post(f"{BASE_URL}/api/transcribe", json=payload) as response:
                if response.status == 200:
                    print("✅ Voice transcription endpoint accessible")
                    return True
                else:
                    print(f"❌ Voice transcription failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Voice transcription error: {e}")
            return False

async def test_weather_service():
    """Test weather service"""
    print("\n🌤️ Testing Weather service...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/api/weather/NewYork") as response:
                if response.status == 200:
                    print("✅ Weather service works")
                    return True
                else:
                    print(f"❌ Weather service failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Weather service error: {e}")
            return False

async def main():
    """Run all tests"""
    print("🚀 Starting CodeVoice Service Tests")
    print("=" * 50)
    
    tests = [
        test_api_gateway_health,
        test_live_ai_coding,
        test_collaborative_docs,
        test_voice_transcription,
        test_weather_service
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Total tests: {len(results)}")
    print(f"   Passed: {sum(results)}")
    print(f"   Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("🎉 All tests passed! Your CodeVoice platform is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the service logs for more details.")
    
    print("\n💡 Next steps:")
    print("   1. Open http://localhost:3000 to see the web interface")
    print("   2. Try the new Live AI Coding and Collaborative Documents tabs")
    print("   3. Test voice commands and real-time collaboration")

if __name__ == "__main__":
    asyncio.run(main()) 