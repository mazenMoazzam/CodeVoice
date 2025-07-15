'use client';

import React, { useState, useEffect, useRef } from 'react';

interface CollaborationProps {
  sessionId?: string;
}

interface User {
  id: string;
  name: string;
  color: string;
}

const Collaboration: React.FC<CollaborationProps> = ({ sessionId: initialSessionId }) => {
  const [sessionId, setSessionId] = useState(initialSessionId || '');
  const [userId, setUserId] = useState('');
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [users, setUsers] = useState<User[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [shareLink, setShareLink] = useState('');
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  
  const wsRef = useRef<WebSocket | null>(null);
  const colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'];

  useEffect(() => {
    // Generate a random user ID if not set
    if (!userId) {
      setUserId(`user_${Math.random().toString(36).substr(2, 9)}`);
    }
  }, [userId]);

  const createSession = async () => {
    setIsCreatingSession(true);
    try {
      const response = await fetch('http://localhost:8000/api/collaboration/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        setShareLink(`${window.location.origin}/collaboration/${data.session_id}`);
        connectToSession(data.session_id);
      }
    } catch (error) {
      console.error('Failed to create session:', error);
    } finally {
      setIsCreatingSession(false);
    }
  };

  const joinSession = (sessionIdToJoin: string) => {
    setSessionId(sessionIdToJoin);
    setShareLink(`${window.location.origin}/collaboration/${sessionIdToJoin}`);
    connectToSession(sessionIdToJoin);
  };

  const connectToSession = (sessionIdToConnect: string) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = new WebSocket(`ws://localhost:8000/api/collaboration/ws/${sessionIdToConnect}/${userId}`);
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('Connected to collaboration session');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'user_joined':
          setUsers(message.users.map((id: string, index: number) => ({
            id,
            name: `User ${index + 1}`,
            color: colors[index % colors.length]
          })));
          if (message.code) {
            setCode(message.code);
          }
          break;
          
        case 'user_left':
          setUsers(message.users.map((id: string, index: number) => ({
            id,
            name: `User ${index + 1}`,
            color: colors[index % colors.length]
          })));
          break;
          
        case 'code_update':
          setCode(message.code);
          setLanguage(message.language);
          break;
          
        case 'voice_command':
          // Handle voice commands in collaboration
          console.log('Voice command received:', message.command);
          break;
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from collaboration session');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    wsRef.current = ws;
  };

  const sendCodeUpdate = (newCode: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'code_update',
        code: newCode,
        language: language
      }));
    }
  };

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newCode = e.target.value;
    setCode(newCode);
    sendCodeUpdate(newCode);
  };

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLanguage = e.target.value;
    setLanguage(newLanguage);
    sendCodeUpdate(code);
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  if (!sessionId) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">👥 Start Collaboration</h2>
          
          <div className="space-y-6">
            <div className="text-center">
              <button
                onClick={createSession}
                disabled={isCreatingSession}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-3 px-6 rounded-lg transition-colors"
              >
                {isCreatingSession ? 'Creating Session...' : 'Create New Session'}
              </button>
            </div>
            
            <div className="text-center">
              <p className="text-gray-600 mb-2">Or join an existing session:</p>
              <div className="flex gap-2 justify-center">
                <input
                  type="text"
                  placeholder="Enter session ID"
                  className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      const input = e.target as HTMLInputElement;
                      if (input.value.trim()) {
                        joinSession(input.value.trim());
                      }
                    }
                  }}
                />
                <button
                  onClick={() => {
                    const input = document.querySelector('input[placeholder="Enter session ID"]') as HTMLInputElement;
                    if (input?.value.trim()) {
                      joinSession(input.value.trim());
                    }
                  }}
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
                >
                  Join
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        {/* Session Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">👥 Collaboration Session</h2>
            <p className="text-gray-600">Session ID: {sessionId}</p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        {/* Share Link */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600 mb-2">Share this link with others:</p>
          <div className="flex gap-2">
            <input
              type="text"
              value={shareLink}
              readOnly
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 bg-white text-sm"
            />
            <button
              onClick={() => navigator.clipboard.writeText(shareLink)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
            >
              Copy
            </button>
          </div>
        </div>

        {/* Online Users */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">Online Users ({users.length})</h3>
          <div className="flex gap-2 flex-wrap">
            {users.map((user) => (
              <div
                key={user.id}
                className="flex items-center gap-2 px-3 py-1 bg-gray-100 rounded-full text-sm"
              >
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: user.color }}
                ></div>
                <span className="text-gray-700">{user.name}</span>
                {user.id === userId && <span className="text-xs text-gray-500">(You)</span>}
              </div>
            ))}
          </div>
        </div>

        {/* Code Editor */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold text-gray-800">Code Editor</h3>
            <select
              value={language}
              onChange={handleLanguageChange}
              className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
              <option value="csharp">C#</option>
            </select>
          </div>
          
          <textarea
            value={code}
            onChange={handleCodeChange}
            placeholder="Start coding together... Use voice commands or type directly."
            className="w-full h-64 border border-gray-300 rounded-lg p-4 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
        </div>

        {/* Voice Integration */}
        <div className="p-4 bg-blue-50 rounded-lg">
          <h4 className="font-semibold text-blue-800 mb-2">🎤 Voice Commands</h4>
          <p className="text-sm text-blue-700">
            Use voice commands to control the collaboration. Try saying "add a function" or "create a class".
          </p>
        </div>
      </div>
    </div>
  );
};

export default Collaboration; 