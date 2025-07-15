'use client';

import React, { useState } from 'react';

interface CodeReviewProps {}

interface ReviewResult {
  overall_score: number;
  summary: string;
  detailed_review: {
    code_quality: { score: number; assessment: string; suggestions: string[] };
    security: { score: number; assessment: string; suggestions: string[] };
    performance: { score: number; assessment: string; suggestions: string[] };
    style: { score: number; assessment: string; suggestions: string[] };
    architecture: { score: number; assessment: string; suggestions: string[] };
  };
  critical_issues: Array<{
    severity: string;
    description: string;
    line: string;
    fix: string;
  }>;
  positive_aspects: string[];
  improvement_areas: string[];
}

const CodeReview: React.FC<CodeReviewProps> = () => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [reviewType, setReviewType] = useState('comprehensive');
  const [isLoading, setIsLoading] = useState(false);
  const [reviewResult, setReviewResult] = useState<ReviewResult | null>(null);
  const [error, setError] = useState('');

  const sampleCode = {
    python: `def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

# Main execution
if __name__ == "__main__":
    print(calculate_fibonacci(10))`,
    javascript: `function calculateFibonacci(n) {
    if (n <= 1) return n;
    return calculateFibonacci(n-1) + calculateFibonacci(n-2);
}

function processData(data) {
    let result = [];
    for (let i = 0; i < data.length; i++) {
        if (data[i] > 0) {
            result.push(data[i] * 2);
        }
    }
    return result;
}

console.log(calculateFibonacci(10));`,
    java: `public class Calculator {
    public static int calculateFibonacci(int n) {
        if (n <= 1) return n;
        return calculateFibonacci(n-1) + calculateFibonacci(n-2);
    }
    
    public static List<Integer> processData(List<Integer> data) {
        List<Integer> result = new ArrayList<>();
        for (Integer item : data) {
            if (item > 0) {
                result.add(item * 2);
            }
        }
        return result;
    }
    
    public static void main(String[] args) {
        System.out.println(calculateFibonacci(10));
    }
}`
  };

  const handleReview = async () => {
    if (!code.trim()) {
      setError('Please enter some code to review');
      return;
    }

    setIsLoading(true);
    setError('');
    setReviewResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/code-review/review', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          language: language,
          review_type: reviewType
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setReviewResult(result);
    } catch (err) {
      setError(`Review failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSampleCode = () => {
    setCode(sampleCode[language as keyof typeof sampleCode] || sampleCode.python);
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 90) return 'bg-green-100';
    if (score >= 80) return 'bg-blue-100';
    if (score >= 70) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">🔍 AI Code Review</h2>
        
        {/* Code Input Section */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Code Input</h3>
            <div className="flex gap-4">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
                <option value="csharp">C#</option>
              </select>
              
              <select
                value={reviewType}
                onChange={(e) => setReviewType(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="comprehensive">Comprehensive</option>
                <option value="security">Security Focus</option>
                <option value="performance">Performance Focus</option>
                <option value="style">Style Focus</option>
              </select>
              
              <button
                onClick={loadSampleCode}
                className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded-lg text-sm transition-colors"
              >
                Load Sample
              </button>
            </div>
          </div>
          
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here for AI-powered review..."
            className="w-full h-64 border border-gray-300 rounded-lg p-4 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
          
          <div className="mt-4 flex justify-between items-center">
            <p className="text-sm text-gray-600">
              {code.length} characters • {code.split('\n').length} lines
            </p>
            
            <button
              onClick={handleReview}
              disabled={isLoading || !code.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-6 rounded-lg transition-colors"
            >
              {isLoading ? 'Reviewing...' : 'Review Code'}
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="mb-6 p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">AI is analyzing your code...</p>
          </div>
        )}

        {/* Review Results */}
        {reviewResult && (
          <div className="space-y-6">
            {/* Overall Score */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-800">Overall Score</h3>
                  <p className="text-gray-600 mt-1">{reviewResult.summary}</p>
                </div>
                <div className={`text-4xl font-bold ${getScoreColor(reviewResult.overall_score)}`}>
                  {reviewResult.overall_score}/100
                </div>
              </div>
            </div>

            {/* Detailed Review */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-800">Detailed Review</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(reviewResult.detailed_review).map(([category, data]) => (
                  <div key={category} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-gray-800 capitalize">
                        {category.replace('_', ' ')}
                      </h4>
                      <span className={`px-2 py-1 rounded text-sm font-semibold ${getScoreBgColor(data.score)} ${getScoreColor(data.score)}`}>
                        {data.score}/100
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{data.assessment}</p>
                    {data.suggestions.length > 0 && (
                      <div>
                        <p className="text-xs font-semibold text-gray-700 mb-1">Suggestions:</p>
                        <ul className="text-xs text-gray-600 space-y-1">
                          {data.suggestions.slice(0, 2).map((suggestion, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-blue-500 mr-1">•</span>
                              {suggestion}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Critical Issues */}
            {reviewResult.critical_issues.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-800">Critical Issues</h3>
                <div className="space-y-3">
                  {reviewResult.critical_issues.map((issue, index) => (
                    <div key={index} className="border-l-4 border-red-500 bg-red-50 p-4 rounded-r-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`px-2 py-1 rounded text-xs font-semibold ${
                              issue.severity === 'high' ? 'bg-red-200 text-red-800' :
                              issue.severity === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                              'bg-blue-200 text-blue-800'
                            }`}>
                              {issue.severity.toUpperCase()}
                            </span>
                            {issue.line && (
                              <span className="text-xs text-gray-500">Line {issue.line}</span>
                            )}
                          </div>
                          <p className="text-sm font-medium text-gray-800 mb-1">{issue.description}</p>
                          {issue.fix && (
                            <p className="text-xs text-gray-600">
                              <span className="font-semibold">Fix:</span> {issue.fix}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Positive Aspects */}
            {reviewResult.positive_aspects.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-800">Positive Aspects</h3>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <ul className="space-y-1">
                    {reviewResult.positive_aspects.map((aspect, index) => (
                      <li key={index} className="flex items-start text-sm text-green-800">
                        <span className="text-green-500 mr-2">✓</span>
                        {aspect}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Improvement Areas */}
            {reviewResult.improvement_areas.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-800">Areas for Improvement</h3>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <ul className="space-y-1">
                    {reviewResult.improvement_areas.map((area, index) => (
                      <li key={index} className="flex items-start text-sm text-yellow-800">
                        <span className="text-yellow-500 mr-2">→</span>
                        {area}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeReview; 