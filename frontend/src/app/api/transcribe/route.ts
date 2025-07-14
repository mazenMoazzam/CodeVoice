import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    console.log('🎵 Received audio transcription request')
    
    const body = await request.json()
    const { audio, language = 'python' } = body
    
    console.log(`📦 Audio data size: ${audio ? audio.length : 0} characters (base64)`)
    console.log(`🔤 Selected language: ${language}`)
    
    // First, transcribe the audio
    const transcriptionResponse = await fetch('http://localhost:8000/api/speech/transcribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        audio_data: audio,
        audio_format: 'webm',
        language: 'en'  // Speech service uses 'en' for English
      })
    })
    
    if (!transcriptionResponse.ok) {
      throw new Error(`Speech service error: ${transcriptionResponse.status}`)
    }
    
    const transcriptionResult = await transcriptionResponse.json()
    console.log('📝 Transcription result:', transcriptionResult)
    
    // Then, generate code from the transcript
    let code = ""
    if (transcriptionResult.transcript && transcriptionResult.transcript.length > 3) {
      const codeResponse = await fetch('http://localhost:8000/api/code/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: transcriptionResult.transcript,
          language: language
        })
      })
      
      if (codeResponse.ok) {
        const codeResult = await codeResponse.json()
        code = codeResult.code
        console.log('🤖 Code generation result:', codeResult)
      } else {
        console.error('❌ Code generation failed:', codeResponse.status)
      }
    }
    
    return NextResponse.json({
      transcript: transcriptionResult.transcript,
      code: code,
      language: language
    })
    
  } catch (error) {
    console.error('❌ Transcription error:', error)
    return NextResponse.json(
      { error: 'Failed to process audio' },
      { status: 500 }
    )
  }
} 