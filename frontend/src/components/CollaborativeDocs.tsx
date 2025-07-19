'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Document {
  id: string;
  title: string;
  content: string;
  language: string;
  createdAt: Date;
  updatedAt: Date;
  collaborators: string[];
}

interface Comment {
  id: string;
  line: number;
  text: string;
  user: string;
  timestamp: Date;
  resolved: boolean;
}

interface User {
  id: string;
  name: string;
  color: string;
  isOnline: boolean;
}

const CollaborativeDocs: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([
    {
      id: '1',
      title: 'React Todo App',
      content: `import React, { useState } from 'react';

const TodoApp = () => {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');

  const addTodo = () => {
    if (input.trim()) {
      setTodos([...todos, { id: Date.now(), text: input, completed: false }]);
      setInput('');
    }
  };

  return (
    <div className="todo-app">
      <h1>Todo List</h1>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Add new todo..."
      />
      <button onClick={addTodo}>Add Todo</button>
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>{todo.text}</li>
        ))}
      </ul>
    </div>
  );
};

export default TodoApp;`,
      language: 'javascript',
      createdAt: new Date(),
      updatedAt: new Date(),
      collaborators: ['You', 'Alice', 'Bob']
    },
    {
      id: '2',
      title: 'Python Data Processing',
      content: `import pandas as pd
import numpy as np

def process_data(data):
    """
    Process the given dataset
    """
    df = pd.DataFrame(data)
    
    # Clean the data
    df = df.dropna()
    
    # Calculate statistics
    stats = {
        'mean': df.mean(),
        'std': df.std(),
        'count': len(df)
    }
    
    return stats

# Example usage
data = [1, 2, 3, 4, 5, None, 7, 8, 9, 10]
result = process_data(data)
print(result)`,
      language: 'python',
      createdAt: new Date(),
      updatedAt: new Date(),
      collaborators: ['You', 'Charlie']
    }
  ]);

  const [currentDoc, setCurrentDoc] = useState<Document | null>(documents[0]);
  const [comments, setComments] = useState<Comment[]>([
    {
      id: '1',
      line: 5,
      text: 'Consider adding input validation here',
      user: 'Alice',
      timestamp: new Date(),
      resolved: false
    },
    {
      id: '2',
      line: 15,
      text: 'Great implementation!',
      user: 'Bob',
      timestamp: new Date(),
      resolved: true
    }
  ]);

  const [activeUsers, setActiveUsers] = useState<User[]>([
    { id: '1', name: 'You', color: '#3B82F6', isOnline: true },
    { id: '2', name: 'Alice', color: '#EF4444', isOnline: true },
    { id: '3', name: 'Bob', color: '#10B981', isOnline: true },
    { id: '4', name: 'Charlie', color: '#F59E0B', isOnline: false }
  ]);

  const [showComments, setShowComments] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [selectedLine, setSelectedLine] = useState<number | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const languages = [
    { value: 'javascript', label: 'JavaScript', icon: '⚡' },
    { value: 'python', label: 'Python', icon: '🐍' },
    { value: 'react', label: 'React', icon: '⚛️' },
    { value: 'typescript', label: 'TypeScript', icon: '📘' },
    { value: 'html', label: 'HTML', icon: '🌐' },
    { value: 'css', label: 'CSS', icon: '🎨' },
  ];

  const handleDocumentChange = (content: string) => {
    if (currentDoc) {
      const updatedDoc = { ...currentDoc, content, updatedAt: new Date() };
      setCurrentDoc(updatedDoc);
      setDocuments(prev => prev.map(doc => doc.id === currentDoc.id ? updatedDoc : doc));
    }
  };

  const addComment = () => {
    if (selectedLine && newComment.trim()) {
      const comment: Comment = {
        id: Date.now().toString(),
        line: selectedLine,
        text: newComment,
        user: 'You',
        timestamp: new Date(),
        resolved: false
      };
      setComments(prev => [...prev, comment]);
      setNewComment('');
      setSelectedLine(null);
    }
  };

  const resolveComment = (commentId: string) => {
    setComments(prev => prev.map(comment => 
      comment.id === commentId ? { ...comment, resolved: true } : comment
    ));
  };

  const createNewDocument = () => {
    const newDoc: Document = {
      id: Date.now().toString(),
      title: 'New Document',
      content: '// Start coding here...',
      language: 'javascript',
      createdAt: new Date(),
      updatedAt: new Date(),
      collaborators: ['You']
    };
    setDocuments(prev => [newDoc, ...prev]);
    setCurrentDoc(newDoc);
  };

  const getLineComments = (lineNumber: number) => {
    return comments.filter(comment => comment.line === lineNumber);
  };

  const renderCodeWithComments = (code: string) => {
    const lines = code.split('\n');
    return lines.map((line, index) => {
      const lineNumber = index + 1;
      const lineComments = getLineComments(lineNumber);
      const hasComments = lineComments.length > 0;
      
      return (
        <div key={index} className="relative group">
          <div 
            className={`flex hover:bg-gray-50 cursor-pointer ${
              selectedLine === lineNumber ? 'bg-blue-50' : ''
            }`}
            onClick={() => setSelectedLine(lineNumber)}
          >
            <div className="w-12 text-right text-gray-500 text-sm pr-2 select-none">
              {lineNumber}
            </div>
            <div className="flex-1 font-mono text-sm">
              {line}
              {hasComments && (
                <span className="ml-2 text-blue-500">💬 {lineComments.length}</span>
              )}
            </div>
          </div>
          
          {/* Inline comments */}
          {hasComments && (
            <div className="ml-12 mb-2">
              {lineComments.map(comment => (
                <div 
                  key={comment.id} 
                  className={`text-sm p-2 rounded border-l-4 ${
                    comment.resolved 
                      ? 'bg-green-50 border-green-400' 
                      : 'bg-yellow-50 border-yellow-400'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-medium text-gray-700">{comment.user}</span>
                      <span className="text-gray-500 ml-2">
                        {comment.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    {!comment.resolved && (
                      <button
                        onClick={() => resolveComment(comment.id)}
                        className="text-xs text-green-600 hover:text-green-800"
                      >
                        Resolve
                      </button>
                    )}
                  </div>
                  <p className="text-gray-700 mt-1">{comment.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      );
    });
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        {/* Header */}
        <div className="border-b border-gray-200 p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">
              📝 Collaborative Documents
            </h2>
            <button
              onClick={createNewDocument}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
            >
              + New Document
            </button>
          </div>
          
          {/* Active Users */}
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">Online collaborators:</span>
            <div className="flex space-x-2">
              {activeUsers.filter(user => user.isOnline).map((user) => (
                <div key={user.id} className="flex items-center space-x-1">
                  <div 
                    className="w-2 h-2 rounded-full" 
                    style={{ backgroundColor: user.color }}
                  ></div>
                  <span className="text-sm text-gray-700">{user.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 p-6">
          {/* Left Panel - Document List */}
          <div className="lg:col-span-1">
            <h3 className="font-semibold text-gray-800 mb-4">Documents</h3>
            <div className="space-y-2">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => setCurrentDoc(doc)}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    currentDoc?.id === doc.id
                      ? 'bg-blue-50 border border-blue-200'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-800">{doc.title}</h4>
                      <p className="text-xs text-gray-500">
                        {languages.find(l => l.value === doc.language)?.label}
                      </p>
                    </div>
                    <span className="text-xs text-gray-400">
                      {doc.collaborators.length} users
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Updated {doc.updatedAt.toLocaleTimeString()}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Center Panel - Code Editor */}
          <div className="lg:col-span-2">
            {currentDoc ? (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <h3 className="font-semibold text-gray-800">{currentDoc.title}</h3>
                    <p className="text-sm text-gray-500">
                      {languages.find(l => l.value === currentDoc.language)?.label} • 
                      Last updated {currentDoc.updatedAt.toLocaleTimeString()}
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setShowComments(!showComments)}
                      className={`px-3 py-1 rounded text-sm ${
                        showComments 
                          ? 'bg-blue-500 text-white' 
                          : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      {showComments ? 'Hide' : 'Show'} Comments
                    </button>
                    <button
                      onClick={() => setIsEditing(!isEditing)}
                      className={`px-3 py-1 rounded text-sm ${
                        isEditing 
                          ? 'bg-green-500 text-white' 
                          : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      {isEditing ? 'View' : 'Edit'}
                    </button>
                  </div>
                </div>

                <div className="bg-gray-900 rounded-lg overflow-hidden">
                  <div className="bg-gray-800 px-4 py-2 flex justify-between items-center">
                    <span className="text-gray-300 text-sm font-medium">
                      {languages.find(l => l.value === currentDoc.language)?.label} Editor
                    </span>
                    <span className="text-gray-400 text-sm">
                      {currentDoc.collaborators.join(', ')} editing
                    </span>
                  </div>
                  
                  {isEditing ? (
                    <textarea
                      value={currentDoc.content}
                      onChange={(e) => handleDocumentChange(e.target.value)}
                      className="w-full h-96 bg-gray-900 text-green-400 p-4 font-mono text-sm resize-none focus:outline-none"
                      placeholder="Start coding..."
                    />
                  ) : (
                    <div className="h-96 overflow-y-auto bg-gray-900 text-green-400 p-4 font-mono text-sm">
                      {showComments ? renderCodeWithComments(currentDoc.content) : currentDoc.content}
                    </div>
                  )}
                </div>

                {/* Add Comment Section */}
                {selectedLine && (
                  <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <h4 className="font-medium text-gray-800 mb-2">
                      Add comment on line {selectedLine}
                    </h4>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        placeholder="Write your comment..."
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <button
                        onClick={addComment}
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                      >
                        Add
                      </button>
                      <button
                        onClick={() => setSelectedLine(null)}
                        className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <p>Select a document to start collaborating</p>
              </div>
            )}
          </div>

          {/* Right Panel - Comments & Activity */}
          <div className="lg:col-span-1">
            <h3 className="font-semibold text-gray-800 mb-4">Comments & Activity</h3>
            
            {/* Recent Comments */}
            <div className="space-y-3 mb-6">
              <h4 className="text-sm font-medium text-gray-700">Recent Comments</h4>
              {comments.slice(0, 5).map((comment) => (
                <div key={comment.id} className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-sm font-medium text-gray-800">{comment.user}</span>
                    <span className="text-xs text-gray-500">
                      {comment.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-1">{comment.text}</p>
                  <p className="text-xs text-gray-500">Line {comment.line}</p>
                </div>
              ))}
            </div>

            {/* Activity Feed */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">Recent Activity</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-gray-600">Alice joined the document</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-gray-600">Bob added a comment</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span className="text-gray-600">You updated line 15</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CollaborativeDocs; 