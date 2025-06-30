'use client'

import { useState, useRef, useEffect } from 'react'

const PROGRAMMING_LANGUAGES = [
  { id: 'python', name: 'Python', icon: '🐍', color: 'from-green-500 to-emerald-600' },
  { id: 'javascript', name: 'JavaScript', icon: '🟨', color: 'from-yellow-400 to-orange-500' },
  { id: 'typescript', name: 'TypeScript', icon: '🔷', color: 'from-blue-500 to-indigo-600' },
  { id: 'java', name: 'Java', icon: '☕', color: 'from-red-500 to-pink-600' },
  { id: 'cpp', name: 'C++', icon: '⚡', color: 'from-purple-500 to-violet-600' },
  { id: 'csharp', name: 'C#', icon: '💎', color: 'from-purple-600 to-indigo-700' },
  { id: 'go', name: 'Go', icon: '🐹', color: 'from-cyan-500 to-blue-600' },
  { id: 'rust', name: 'Rust', icon: '🦀', color: 'from-orange-500 to-red-600' },
  { id: 'php', name: 'PHP', icon: '🐘', color: 'from-purple-400 to-pink-500' },
  { id: 'ruby', name: 'Ruby', icon: '💎', color: 'from-red-400 to-pink-500' },
  { id: 'swift', name: 'Swift', icon: '🍎', color: 'from-orange-400 to-red-500' },
  { id: 'kotlin', name: 'Kotlin', icon: '🟦', color: 'from-purple-500 to-indigo-600' },
]

export default function VoiceButton() {
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [code, setCode] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [isClient, setIsClient] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState('python')
  const [showLanguageSelector, setShowLanguageSelector] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const [recordingTime, setRecordingTime] = useState(0)
  const [showSuccess, setShowSuccess] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const volumeIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const timeIntervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    setIsClient(true)
  }, [])

  const startRecording = async () => {
    try {
      console.log('🎤 Starting recording...')
      
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      })

      audioContextRef.current = new AudioContext()
      analyserRef.current = audioContextRef.current.createAnalyser()
      const source = audioContextRef.current.createMediaStreamSource(stream)
      source.connect(analyserRef.current)

      volumeIntervalRef.current = setInterval(() => {
        if (analyserRef.current) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
          analyserRef.current.getByteFrequencyData(dataArray)
          const volume = Math.round(dataArray.reduce((a, b) => a + b) / dataArray.length)
          setAudioLevel(volume)
        }
      }, 100)

      setRecordingTime(0)
      timeIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)

      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })

      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
          console.log(`📦 Audio chunk received: ${event.data.size} bytes`)
        }
      }

      mediaRecorderRef.current.onstop = async () => {
        console.log('🛑 Recording stopped, processing audio...')
        setIsProcessing(true)
        
        if (volumeIntervalRef.current) {
          clearInterval(volumeIntervalRef.current)
          volumeIntervalRef.current = null
        }
        if (timeIntervalRef.current) {
          clearInterval(timeIntervalRef.current)
          timeIntervalRef.current = null
        }
        
        try {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
          console.log(`🎵 Total audio size: ${audioBlob.size} bytes`)
          
          const response = await fetch('/api/transcribe', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              audio: await blobToBase64(audioBlob),
              language: selectedLanguage
            })
          })
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const result = await response.json()
          console.log('📝 Received result:', result)
          
          if (result.transcript) {
            setTranscript(result.transcript)
          }
          
          if (result.code) {
            setCode(result.code)
            setShowSuccess(true)
            setTimeout(() => setShowSuccess(false), 3000)
          }
          
        } catch (error) {
          console.error('❌ Error processing audio:', error)
          setTranscript('Error processing audio. Please try again.')
        } finally {
          setIsProcessing(false)
        }
        
        stream.getTracks().forEach(track => track.stop())
        if (audioContextRef.current?.state !== 'closed') {
          audioContextRef.current?.close()
        }
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
      setTranscript('')
      setCode('')

    } catch (error) {
      console.error('❌ Error starting recording:', error)
      alert('Error accessing microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      console.log('🛑 Stopping recording...')
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        const result = reader.result as string
        resolve(result.split(',')[1]) 
      }
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  }

  const selectedLanguageInfo = PROGRAMMING_LANGUAGES.find(lang => lang.id === selectedLanguage)
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (!isClient) {
    return (
      <div className="flex items-center justify-center min-h-[200px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent animate-gradient-shift">
          CodeVoice
        </h1>
        <p className="text-gray-600 text-lg">
          Speak your code into reality with AI-powered voice-to-code generation
        </p>
        
        {/* Floating particles */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-10 left-10 w-2 h-2 bg-blue-400 rounded-full animate-float" style={{ animationDelay: '0s' }}></div>
          <div className="absolute top-20 right-20 w-3 h-3 bg-purple-400 rounded-full animate-float" style={{ animationDelay: '1s' }}></div>
          <div className="absolute bottom-20 left-20 w-2 h-2 bg-green-400 rounded-full animate-float" style={{ animationDelay: '2s' }}></div>
          <div className="absolute bottom-10 right-10 w-3 h-3 bg-yellow-400 rounded-full animate-float" style={{ animationDelay: '0.5s' }}></div>
        </div>
      </div>

      {/* Main Controls */}
      <div className="flex flex-col lg:flex-row items-center gap-6 p-8 bg-gradient-to-br from-gray-50 to-white rounded-2xl shadow-lg border border-gray-100 hover-lift">
        {/* Language Selector */}
        <div className="relative">
          <button
            onClick={() => setShowLanguageSelector(!showLanguageSelector)}
            className={`flex items-center gap-3 px-6 py-4 bg-gradient-to-r ${selectedLanguageInfo?.color} text-white rounded-xl hover:scale-105 transition-all duration-200 shadow-lg hover-lift`}
          >
            <span className="text-2xl">{selectedLanguageInfo?.icon}</span>
            <span className="font-semibold text-lg">{selectedLanguageInfo?.name}</span>
            <span className={`transition-transform duration-200 ${showLanguageSelector ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </button>
          
          {showLanguageSelector && (
            <div className="absolute top-full left-0 mt-3 bg-white border border-gray-200 rounded-xl shadow-xl z-10 max-h-80 overflow-y-auto w-64 animate-fade-in">
              {PROGRAMMING_LANGUAGES.map((language) => (
                <button
                  key={language.id}
                  onClick={() => {
                    setSelectedLanguage(language.id)
                    setShowLanguageSelector(false)
                  }}
                  className={`flex items-center gap-3 w-full px-4 py-3 hover:bg-gray-50 transition-all duration-150 hover-lift ${
                    selectedLanguage === language.id ? 'bg-blue-50 text-blue-600' : ''
                  }`}
                >
                  <span className="text-xl">{language.icon}</span>
                  <span className="font-medium">{language.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Voice Button */}
        <div className="relative">
          <button
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onMouseLeave={stopRecording}
            disabled={isProcessing}
            className={`relative p-8 rounded-full transition-all duration-300 ${
              isProcessing
                ? 'bg-gradient-to-r from-yellow-400 to-orange-500 cursor-wait scale-95'
                : isRecording
                ? 'bg-gradient-to-r from-red-500 to-pink-600 animate-pulse scale-110 animate-pulse-glow'
                : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:scale-105 hover:shadow-2xl'
            } text-white shadow-lg hover-lift`}
          >
            <span className="text-4xl">
              {isProcessing ? '⏳' : isRecording ? '🛑' : '🎤'}
            </span>
            
            {/* Recording Animation */}
            {isRecording && (
              <>
                <div className="absolute inset-0 rounded-full border-4 border-white/30 animate-ping"></div>
                <div className="absolute inset-0 rounded-full border-2 border-white/50 animate-ping" style={{ animationDelay: '0.5s' }}></div>
              </>
            )}
          </button>
          
          {/* Audio Level Indicator */}
          {isRecording && (
            <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-green-400 to-blue-500 transition-all duration-100"
                style={{ width: `${Math.min(100, audioLevel)}%` }}
              />
            </div>
          )}
        </div>

        {/* Recording Timer */}
        {isRecording && (
          <div className="text-center animate-fade-in">
            <div className="text-2xl font-mono font-bold text-gray-700">
              {formatTime(recordingTime)}
            </div>
            <div className="text-sm text-gray-500">Recording...</div>
          </div>
        )}

        {/* Processing Indicator */}
        {isProcessing && (
          <div className="flex items-center gap-3 text-gray-600 animate-fade-in">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span className="font-medium">Processing audio<span className="loading-dots"></span></span>
          </div>
        )}
      </div>

      {/* Success Message */}
      {showSuccess && (
        <div className="fixed top-4 right-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-3 rounded-lg shadow-lg animate-slide-in-right z-50 hover-lift">
          <div className="flex items-center gap-2">
            <span className="text-xl">✅</span>
            <span>Code generated successfully!</span>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-100 hover-lift">
        <div className="flex items-start gap-3">
          <span className="text-2xl animate-float">💡</span>
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Pro Tips:</h3>
            <ul className="text-gray-600 space-y-1 text-sm">
              <li>• Speak clearly and at a normal pace</li>
              <li>• Be specific about what you want to create</li>
              <li>• Try: "Create a function to reverse a string in {selectedLanguageInfo?.name}"</li>
              <li>• Hold the button while speaking, release when done</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Results */}
      {transcript && (
        <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 animate-fade-in hover-lift">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xl">📝</span>
            <h3 className="font-semibold text-gray-800">Transcript</h3>
          </div>
          <p className="text-gray-700 bg-gray-50 p-4 rounded-lg">{transcript}</p>
        </div>
      )}

      {code && (
        <div className="bg-gray-900 p-6 rounded-xl shadow-lg border border-gray-700 animate-fade-in hover-lift">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <span className="text-xl">💻</span>
              <h3 className="font-semibold text-gray-200">Generated {selectedLanguageInfo?.name} Code</h3>
            </div>
            <button
              onClick={() => {
                navigator.clipboard.writeText(code)
                setShowSuccess(true)
                setTimeout(() => setShowSuccess(false), 2000)
              }}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm text-gray-200 transition-colors flex items-center gap-2 hover-lift"
            >
              <span>📋</span>
              Copy Code
            </button>
          </div>
          <pre className="text-green-400 font-mono text-sm overflow-x-auto bg-gray-800 p-4 rounded-lg border border-gray-700">
            {code}
          </pre>
        </div>
      )}
    </div>
  )
}