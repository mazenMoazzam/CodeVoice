'use client'

import { useState, useRef, useEffect } from 'react'

export default function VoiceButton() {
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [code, setCode] = useState('')
  const [isClient, setIsClient] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const wsRef = useRef<WebSocket | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const volumeIntervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    setIsClient(true)
    return () => {
      // Cleanup
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (volumeIntervalRef.current) {
        clearInterval(volumeIntervalRef.current)
      }
      if (audioContextRef.current?.state !== 'closed') {
        audioContextRef.current?.close()
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: false,
          noiseSuppression: true,
          autoGainControl: true
        },
        video: false
      })

      // Initialize WebSocket
      wsRef.current = new WebSocket('ws://localhost:8000/ws')

      // Setup audio analysis
      audioContextRef.current = new AudioContext()
      analyserRef.current = audioContextRef.current.createAnalyser()
      const source = audioContextRef.current.createMediaStreamSource(stream)
      source.connect(analyserRef.current)

      // Monitor audio levels
      volumeIntervalRef.current = setInterval(() => {
        if (analyserRef.current) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
          analyserRef.current.getByteFrequencyData(dataArray)
          const volume = Math.round(dataArray.reduce((a, b) => a + b) / dataArray.length)
          setAudioLevel(volume)
          console.log('Audio level:', volume)
        }
      }, 200)

      // Configure MediaRecorder with proper audio format
      const options = {
        audioBitsPerSecond: 16000,
        mimeType: 'audio/webm;codecs=opus'
      }

      mediaRecorderRef.current = new MediaRecorder(stream, options)

      // Handle audio data chunks
      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
          const reader = new FileReader()
          reader.onload = () => {
            if (reader.result instanceof ArrayBuffer) {
              // Add header with audio metadata
              const header = new DataView(new ArrayBuffer(4))
              header.setUint32(0, reader.result.byteLength, true)

              // Combine header and audio data
              const combined = new Uint8Array(header.byteLength + reader.result.byteLength)
              combined.set(new Uint8Array(header.buffer), 0)
              combined.set(new Uint8Array(reader.result), header.byteLength)

              wsRef.current?.send(combined)
            }
          }
          reader.readAsArrayBuffer(e.data)
        }
      }

      // Handle WebSocket messages
      wsRef.current.onmessage = (e) => {
        const data = e.data
        if (data.startsWith('TRANSCRIPT:')) {
          setTranscript(data.replace('TRANSCRIPT:', ''))
        } else if (data.startsWith('CODE:')) {
          setCode(data.replace('CODE:', ''))
        }
      }

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        stopRecording()
      }

      // Start recording
      mediaRecorderRef.current.start(200)
      setIsRecording(true)

    } catch (err) {
      console.error('Recording setup error:', err)
      setIsRecording(false)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
    }
    if (volumeIntervalRef.current) {
      clearInterval(volumeIntervalRef.current)
      volumeIntervalRef.current = null
    }
    if (audioContextRef.current?.state !== 'closed') {
      audioContextRef.current?.close()
    }
    setIsRecording(false)
    setAudioLevel(0)
  }

  if (!isClient) {
    return (
      <button
        disabled
        className="p-4 rounded-full bg-gray-500 text-white opacity-50"
      >
        Loading voice service...
      </button>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <button
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          className={`p-4 rounded-full ${
            isRecording
              ? 'bg-red-500 animate-pulse'
              : 'bg-blue-500 hover:bg-blue-600'
          } text-white transition-all`}
        >
          {isRecording ? '🛑 Stop Recording' : '🎤 Hold to Speak'}
        </button>
        {isRecording && (
          <div className="w-32 h-4 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all"
              style={{ width: `${Math.min(100, audioLevel)}%` }}
            />
          </div>
        )}
      </div>

      {transcript && (
        <div className="p-4 bg-gray-100 rounded-lg">
          <p className="font-medium">Transcript:</p>
          <p>{transcript}</p>
        </div>
      )}

      {code && (
        <div className="p-4 bg-gray-800 rounded-lg text-green-400 font-mono overflow-x-auto">
          <pre>{code}</pre>
          <button
            onClick={() => navigator.clipboard.writeText(code)}
            className="mt-2 px-3 py-1 bg-gray-700 rounded text-sm hover:bg-gray-600"
          >
            Copy Code
          </button>
        </div>
      )}
    </div>
  )
}