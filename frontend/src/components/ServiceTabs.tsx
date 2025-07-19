'use client';

import React, { useState } from 'react';
import VoiceToCode from './VoiceButton';
import CodeReview from './CodeReview';
import Collaboration from './Collaboration';
import LiveAICoding from './LiveAICoding';
import CollaborativeDocs from './CollaborativeDocs';

const ServiceTabs: React.FC = () => {
  const [activeTab, setActiveTab] = useState('voice-to-code');

  const tabs = [
    { id: 'voice-to-code', label: '🎤 Voice-to-Code', icon: '🎤' },
    { id: 'code-review', label: '🔍 Code Review', icon: '🔍' },
    { id: 'collaboration', label: '👥 Collaboration', icon: '👥' },
    { id: 'live-ai-coding', label: '🤖 Live AI Coding', icon: '🤖' },
    { id: 'collaborative-docs', label: '📝 Collaborative Docs', icon: '📝' },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'voice-to-code':
        return <VoiceToCode />;
      case 'code-review':
        return <CodeReview />;
      case 'collaboration':
        return <Collaboration />;
      case 'live-ai-coding':
        return <LiveAICoding />;
      case 'collaborative-docs':
        return <CollaborativeDocs />;
      default:
        return <VoiceToCode />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 mb-8">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow-lg">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default ServiceTabs; 