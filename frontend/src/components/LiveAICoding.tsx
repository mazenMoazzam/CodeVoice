'use client';

import React, { useState, useRef, useEffect } from 'react';

interface CodeBlock {
  id: string;
  code: string;
  language: string;
  timestamp: Date;
  user: string;
  isAI: boolean;
}

interface Comment {
  id: string;
  line: number;
  text: string;
  user: string;
  timestamp: Date;
}

const LiveAICoding: React.FC = () => {
  const [isListening, setIsListening] = useState(false);
  const [currentCode, setCurrentCode] = useState('');
  const [language, setLanguage] = useState('javascript');
  const [codeBlocks, setCodeBlocks] = useState<CodeBlock[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState('Ready for AI-powered coding');
  const [activeUsers, setActiveUsers] = useState(['You', 'Alice', 'Bob']);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const languages = [
    { value: 'javascript', label: 'JavaScript', icon: '⚡' },
    { value: 'python', label: 'Python', icon: '🐍' },
    { value: 'react', label: 'React', icon: '⚛️' },
    { value: 'typescript', label: 'TypeScript', icon: '📘' },
    { value: 'html', label: 'HTML', icon: '🌐' },
    { value: 'css', label: 'CSS', icon: '🎨' },
  ];

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        setIsProcessing(true);
        try {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const base64Audio = await blobToBase64(audioBlob);
          
          const response = await fetch('/api/transcribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ audio: base64Audio, language: 'en' })
          });

          if (response.ok) {
            const result = await response.json();
            if (result.transcript) {
              handleVoiceCommand(result.transcript);
            }
          }
        } catch (error) {
          console.error('Error processing audio:', error);
        } finally {
          setIsProcessing(false);
        }
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsListening(true);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isListening) {
      mediaRecorderRef.current.stop();
      setIsListening(false);
    }
  };

  const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        resolve(result.split(',')[1]);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  const handleVoiceCommand = async (transcript: string) => {
    setStatus('🤖 AI is generating code...');

    // Simulate AI code generation
    const aiResponse = await generateAICode(transcript, language);
    
    const newCodeBlock: CodeBlock = {
      id: Date.now().toString(),
      code: aiResponse.code,
      language: language,
      timestamp: new Date(),
      user: 'AI Assistant',
      isAI: true
    };

    setCodeBlocks(prev => [newCodeBlock, ...prev]);
    setCurrentCode(aiResponse.code);
    setStatus(`✅ Generated ${language} code: "${transcript}"`);
  };

  const generateAICode = async (command: string, lang: string): Promise<{ code: string }> => {
    // Simulate AI processing delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    const commandLower = command.toLowerCase();
    
    if (lang === 'javascript') {
      if (commandLower.includes('function') || commandLower.includes('create')) {
        return {
          code: `function ${commandLower.includes('todo') ? 'addTodo' : 'processData'}(data) {
  // Process the data
  const result = data.map(item => ({
    id: item.id,
    name: item.name,
    processed: true
  }));
  
  return result;
}

// Usage example
const data = [{ id: 1, name: 'Item 1' }];
const processed = ${commandLower.includes('todo') ? 'addTodo' : 'processData'}(data);
console.log(processed);`
        };
      } else if (commandLower.includes('react') || commandLower.includes('component')) {
        return {
          code: `import React, { useState } from 'react';

const ${commandLower.includes('todo') ? 'TodoList' : 'MyComponent'} = () => {
  const [items, setItems] = useState([]);
  const [input, setInput] = useState('');

  const addItem = () => {
    if (input.trim()) {
      setItems([...items, { id: Date.now(), text: input }]);
      setInput('');
    }
  };

  return (
    <div className="todo-container">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Add new item..."
      />
      <button onClick={addItem}>Add</button>
      <ul>
        {items.map(item => (
          <li key={item.id}>{item.text}</li>
        ))}
      </ul>
    </div>
  );
};

export default ${commandLower.includes('todo') ? 'TodoList' : 'MyComponent'};`
        };
      }
    } else if (lang === 'python') {
      if (commandLower.includes('function') || commandLower.includes('create')) {
        return {
          code: `def ${commandLower.includes('process') ? 'process_data' : 'calculate_sum'}(data):
    """
    Process the given data
    """
    if isinstance(data, list):
        return sum(data) if 'sum' in '${commandLower}' else len(data)
    return data

# Example usage
data = [1, 2, 3, 4, 5]
result = ${commandLower.includes('process') ? 'process_data' : 'calculate_sum'}(data)
print(f"Result: {result}")`
        };
      }
    }

    // Default response
    return {
      code: `// Generated code for: "${command}"
// Language: ${lang}
// TODO: Implement the requested functionality

console.log("Hello from AI-generated code!");`
    };
  };

  const addComment = (line: number, text: string) => {
    const newComment: Comment = {
      id: Date.now().toString(),
      line,
      text,
      user: 'You',
      timestamp: new Date()
    };
    setComments(prev => [...prev, newComment]);
  };

  const copyToClipboard = (code: string) => {
    navigator.clipboard.writeText(code);
    setStatus('📋 Code copied to clipboard!');
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        {/* Header */}
        <div className="border-b border-gray-200 p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            🤖 Live AI Coding Assistant
          </h2>
          <p className="text-gray-600 mb-4">
            Code with AI using voice commands. Speak naturally and watch AI generate code in real-time!
          </p>
          
          {/* Active Users */}
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">Active users:</span>
            <div className="flex space-x-2">
              {activeUsers.map((user, index) => (
                <div key={index} className="flex items-center space-x-1">
                  <div className={`w-2 h-2 rounded-full ${index === 0 ? 'bg-green-500' : 'bg-blue-500'}`}></div>
                  <span className="text-sm text-gray-700">{user}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
          {/* Left Panel - Voice Control & Language Selection */}
          <div className="lg:col-span-1 space-y-6">
            {/* Language Selection */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-800 mb-3">Programming Language</h3>
              <div className="grid grid-cols-2 gap-2">
                {languages.map((lang) => (
                  <button
                    key={lang.value}
                    onClick={() => setLanguage(lang.value)}
                    className={`p-3 rounded-lg text-sm font-medium transition-all ${
                      language === lang.value
                        ? 'bg-blue-500 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span className="mr-2">{lang.icon}</span>
                    {lang.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Voice Control */}
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 p-6 rounded-lg border border-blue-200">
              <h3 className="font-semibold text-blue-800 mb-4">🎤 Voice Commands</h3>
              <div className="text-center mb-4">
                <button
                  onMouseDown={startRecording}
                  onMouseUp={stopRecording}
                  onMouseLeave={stopRecording}
                  disabled={isProcessing}
                  className={`relative p-6 rounded-full transition-all duration-300 ${
                    isProcessing
                      ? 'bg-gradient-to-r from-yellow-400 to-orange-500 cursor-wait'
                      : isListening
                      ? 'bg-gradient-to-r from-red-500 to-pink-600 animate-pulse'
                      : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:scale-105'
                  } text-white shadow-lg`}
                >
                  <span className="text-3xl">
                    {isProcessing ? '⏳' : isListening ? '🛑' : '🎤'}
                  </span>
                </button>
              </div>
              <p className="text-sm text-blue-700 text-center">
                Click and hold to speak your coding request
              </p>
            </div>

            {/* Quick Commands */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-800 mb-3">💡 Quick Commands</h3>
              <div className="space-y-2">
                <button
                  onClick={() => handleVoiceCommand('Create a React todo component')}
                  className="w-full text-left p-2 rounded bg-white hover:bg-gray-100 text-sm"
                >
                  "Create a React todo component"
                </button>
                <button
                  onClick={() => handleVoiceCommand('Write a JavaScript function to process data')}
                  className="w-full text-left p-2 rounded bg-white hover:bg-gray-100 text-sm"
                >
                  "Write a JavaScript function to process data"
                </button>
                <button
                  onClick={() => handleVoiceCommand('Create a Python function to calculate sum')}
                  className="w-full text-left p-2 rounded bg-white hover:bg-gray-100 text-sm"
                >
                  "Create a Python function to calculate sum"
                </button>
              </div>
            </div>
          </div>

          {/* Right Panel - Code Editor & History */}
          <div className="lg:col-span-2 space-y-6">
            {/* Current Code Editor */}
            <div className="bg-gray-900 rounded-lg overflow-hidden">
              <div className="bg-gray-800 px-4 py-2 flex justify-between items-center">
                <span className="text-gray-300 text-sm font-medium">
                  {languages.find(l => l.value === language)?.label} Editor
                </span>
                <button
                  onClick={() => copyToClipboard(currentCode)}
                  className="text-gray-400 hover:text-white text-sm"
                >
                  📋 Copy
                </button>
              </div>
              <textarea
                value={currentCode}
                onChange={(e) => setCurrentCode(e.target.value)}
                className="w-full h-64 bg-gray-900 text-green-400 p-4 font-mono text-sm resize-none focus:outline-none"
                placeholder="AI-generated code will appear here..."
              />
            </div>

            {/* Status */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-800 mb-2">Status</h3>
              <p className="text-blue-700">{status}</p>
            </div>

            {/* Code History */}
            <div>
              <h3 className="font-semibold text-gray-800 mb-4">📚 Code History</h3>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {codeBlocks.map((block) => (
                  <div key={block.id} className="border rounded-lg p-4 bg-gray-50">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm ${block.isAI ? 'text-purple-600' : 'text-blue-600'}`}>
                          {block.isAI ? '🤖 AI' : '👤 You'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {block.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <button
                        onClick={() => setCurrentCode(block.code)}
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        Load
                      </button>
                    </div>
                    <pre className="text-xs bg-white p-2 rounded border overflow-x-auto">
                      <code>{block.code.substring(0, 100)}...</code>
                    </pre>
                  </div>
                ))}
                {codeBlocks.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <p>No code generated yet. Try a voice command!</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveAICoding; 