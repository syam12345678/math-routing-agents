import React, { useState } from 'react';

const ResponseDisplay = ({ response }) => {
  const [showSteps, setShowSteps] = useState(true);

  if (!response) return null;

  const { solution, steps, method, confidence, sources, routing_source } = response;

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">🎯</span>
            <div>
              <h3 className="text-lg font-semibold">Solution Found</h3>
              <p className="text-sm opacity-90">Method: {method}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm opacity-90">Confidence</div>
            <div className="text-xl font-bold">
              {Math.round(confidence * 100)}%
            </div>
          </div>
        </div>
      </div>

      {/* Solution */}
      <div className="p-6">
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
            <span className="text-xl mr-2">💡</span>
            Solution
          </h4>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-gray-800 leading-relaxed">{solution}</p>
          </div>
        </div>

        {/* Steps Toggle */}
        {steps && steps.length > 0 && (
          <div className="mb-6">
            <button
              onClick={() => setShowSteps(!showSteps)}
              className="flex items-center space-x-2 text-indigo-600 hover:text-indigo-700 font-medium mb-3"
            >
              <span className="text-lg">
                {showSteps ? '📖' : '📚'}
              </span>
              <span>
                {showSteps ? 'Hide' : 'Show'} Step-by-Step Solution
              </span>
              <svg 
                className={`w-4 h-4 transition-transform duration-200 ${showSteps ? 'rotate-180' : ''}`}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showSteps && (
              <div className="space-y-3">
                {steps.map((step, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                    <div className="flex-shrink-0 w-6 h-6 bg-indigo-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                      {index + 1}
                    </div>
                    <p className="text-gray-700 flex-1">{step}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-200">
          <div>
            <h5 className="text-sm font-semibold text-gray-600 mb-2">Routing Information</h5>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                routing_source === 'knowledge_base' 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-blue-100 text-blue-700'
              }`}>
                {routing_source === 'knowledge_base' ? 'Knowledge Base' : 'Web Search'}
              </span>
            </div>
          </div>
          
          <div>
            <h5 className="text-sm font-semibold text-gray-600 mb-2">Sources</h5>
            <div className="space-y-1">
              {sources && sources.map((source, index) => (
                <div key={index} className="text-sm text-gray-600 flex items-center">
                  <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full mr-2"></span>
                  {source}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResponseDisplay;