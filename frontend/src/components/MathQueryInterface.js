import React, { useState } from 'react';
import QueryInput from './QueryInput';
import ResponseDisplay from './ResponseDisplay';

const MathQueryInterface = ({ onSubmit, isLoading, recentQueries }) => {
  const [currentResponse, setCurrentResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (question) => {
    setError(null);
    setCurrentResponse(null);
    
    const result = await onSubmit(question);
    
    if (result.success) {
      setCurrentResponse(result.data);
    } else {
      setError(result.error);
    }
  };

  const exampleQueries = [
    "Solve the quadratic equation: x² - 5x + 6 = 0",
    "Find the derivative of f(x) = x³ + 2x² - 5x + 3",
    "Calculate the area of a circle with radius 5 cm",
    "Evaluate the integral: ∫(2x + 1)dx",
    "Find sin(30°) using special triangles",
    "Find the mean of the dataset: [2, 4, 6, 8, 10]"
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Query Interface */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
              <span className="text-3xl mr-3">🧮</span>
              Math Problem Solver
            </h2>
            <p className="text-gray-600 mb-6">
              Ask any mathematical question and get step-by-step solutions with intelligent routing.
            </p>
            
            <QueryInput onSubmit={handleSubmit} isLoading={isLoading} />
            
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center">
                  <span className="text-red-500 text-xl mr-2">⚠️</span>
                  <span className="text-red-700 font-medium">Error:</span>
                </div>
                <p className="text-red-600 mt-1">{error}</p>
              </div>
            )}
            
            {currentResponse && (
              <div className="mt-6">
                <ResponseDisplay response={currentResponse} />
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Example Queries */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="text-xl mr-2">💡</span>
              Try These Examples
            </h3>
            <div className="space-y-3">
              {exampleQueries.map((query, index) => (
                <button
                  key={index}
                  onClick={() => handleSubmit(query)}
                  disabled={isLoading}
                  className="w-full text-left p-3 bg-gray-50 hover:bg-indigo-50 rounded-lg text-sm text-gray-700 hover:text-indigo-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>

          {/* Recent Queries */}
          {recentQueries.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <span className="text-xl mr-2">🕒</span>
                Recent Queries
              </h3>
              <div className="space-y-3">
                {recentQueries.map((query) => (
                  <div
                    key={query.id}
                    className="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-indigo-50 transition-colors duration-200"
                    onClick={() => setCurrentResponse(query)}
                  >
                    <p className="text-sm text-gray-700 line-clamp-2">{query.question}</p>
                    <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                      <span className={`px-2 py-1 rounded-full ${
                        query.routing === 'knowledge_base' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        {query.routing === 'knowledge_base' ? 'Knowledge Base' : 'Web Search'}
                      </span>
                      <span>{(query.confidence * 100).toFixed(0)}% confidence</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* System Features */}
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="text-xl mr-2">⚡</span>
              System Features
            </h3>
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                Intelligent Query Routing
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                Step-by-Step Solutions
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                Human-in-the-Loop Learning
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-orange-500 rounded-full mr-3"></span>
                Confidence Scoring
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MathQueryInterface;