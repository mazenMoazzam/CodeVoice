import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    console.log('🎵 Received audio transcription request')
    
    const body = await request.json()
    const { audio, language = 'python' } = body
    
    console.log(`📦 Audio data size: ${audio ? audio.length : 0} characters (base64)`)
    console.log(`🔤 Selected language: ${language}`)
    
    const backendResponse = await fetch('http://localhost:8000/transcribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        audio_data: audio,
        audio_format: 'webm',
        language: language
      })
    })
    
    if (!backendResponse.ok) {
      throw new Error(`Backend error: ${backendResponse.status}`)
    }
    
    const result = await backendResponse.json()
    console.log('✅ Backend response:', result)
    
    return NextResponse.json(result)
    
  } catch (error) {
    console.error('❌ Transcription error:', error)
    return NextResponse.json(
      { error: 'Failed to process audio' },
      { status: 500 }
    )
  }
} 