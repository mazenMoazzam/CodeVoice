'use client';

import { useState } from 'react';
import VoiceButton from '@/components/VoiceButton';
import ServiceTabs from '@/components/ServiceTabs';

export default function Home() {
  const [activeTab, setActiveTab] = useState('voice-to-code');

  const renderActiveService = () => {
    switch (activeTab) {
      case 'voice-to-code':
        return <VoiceButton />;
      case 'code-review':
        return (
          <div className="max-w-4xl mx-auto p-6">
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">🔍 Code Review Service</h2>
              <p className="text-gray-600 mb-6">AI-powered code analysis and review coming soon!</p>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-yellow-800 text-sm">
                  This service will provide automated code review, security analysis, and performance optimization suggestions.
                </p>
              </div>
            </div>
          </div>
        );
      case 'analytics':
        return (
          <div className="max-w-4xl mx-auto p-6">
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">📊 Analytics Service</h2>
              <p className="text-gray-600 mb-6">Usage metrics and performance analytics coming soon!</p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-blue-800 text-sm">
                  This service will track usage patterns, code generation statistics, and system performance metrics.
                </p>
              </div>
            </div>
          </div>
        );
      default:
        return <VoiceButton />;
    }
  };

  return (
    <main className="min-h-screen p-6 lg:p-24">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">CodeVoice AI Platform</h1>
        
        <ServiceTabs activeTab={activeTab} onTabChange={setActiveTab} />
        
        {renderActiveService()}
      </div>
    </main>
  );
}