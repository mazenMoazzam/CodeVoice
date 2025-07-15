'use client';

import React, { useState } from 'react';

interface ServiceTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const ServiceTabs: React.FC<ServiceTabsProps> = ({ activeTab, onTabChange }) => {
  const tabs = [
    {
      id: 'voice-to-code',
      name: '🎤 Voice-to-Code',
      description: 'Convert voice commands to code'
    },
    {
      id: 'code-review',
      name: '🔍 Code Review',
      description: 'AI-powered code analysis (coming soon)'
    },
    {
      id: 'analytics',
      name: '📊 Analytics',
      description: 'Usage and performance metrics (coming soon)'
    }
  ];

  return (
    <div className="w-full mb-6">
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm
                ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>
      
      {/* Tab Description */}
      <div className="mt-2">
        <p className="text-sm text-gray-600">
          {tabs.find(tab => tab.id === activeTab)?.description}
        </p>
      </div>
    </div>
  );
};

export default ServiceTabs; 