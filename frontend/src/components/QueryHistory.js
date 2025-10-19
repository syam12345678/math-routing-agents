import React, { useState } from 'react';

const QueryHistory = ({ queries, onClear }) => {
  const [selectedQuery, setSelectedQuery] = useState(null);
  const [filter, setFilter] = useState('all');

  const filteredQueries = queries.filter(query => {
    if (filter === 'all') return true;
    return query.routing === filter;
  });

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-600 bg-green-100';
    if (confidence >= 0.7) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2 flex items-center">
              <span className="text-3xl mr-3">📚</span>
              Query History
            </h2>
            <p className="text-gray-600">
              View and analyze your previous mathematical queries and solutions.
            </p>
          </div>
          
          {queries.length > 0 && (
            <div className="mt-4 sm:mt-0 flex space-x-3">
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="all">All Queries</option>
                <option value="knowledge_base">Knowledge Base</option>
                <option value="web_search">Web Search</option>
              </select>
              
              <button
                onClick={onClear}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
              >
                Clear History
              </button>
            </div>
          )}
        </div>

        {queries.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-600 mb-2">No queries yet</h3>
            <p className="text-gray-500">Start solving math problems to see your history here.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredQueries.map((query) => (
              <div
                key={query.id}
                className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                  selectedQuery?.id === query.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                }`}
                onClick={() => setSelectedQuery(selectedQuery?.id === query.id ? null : query)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-800 mb-2 line-clamp-2">
                      {query.question}
                    </h4>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{formatDate(query.timestamp)}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        query.routing === 'knowledge_base' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        {query.routing === 'knowledge_base' ? 'Knowledge Base' : 'Web Search'}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(query.confidence)}`}>
                        {Math.round(query.confidence * 100)}% confidence
                      </span>
                    </div>
                  </div>
                  
                  <div className="ml-4">
                    <svg 
                      className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
                        selectedQuery?.id === query.id ? 'rotate-180' : ''
                      }`}
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>

                {/* Expanded Details */}
                {selectedQuery?.id === query.id && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="space-y-4">
                      <div>
                        <h5 className="font-medium text-gray-700 mb-2">Solution:</h5>
                        <p className="text-gray-600 bg-gray-50 p-3 rounded-lg">
                          {query.response.solution}
                        </p>
                      </div>
                      
                      {query.response.steps && query.response.steps.length > 0 && (
                        <div>
                          <h5 className="font-medium text-gray-700 mb-2">Steps:</h5>
                          <div className="space-y-2">
                            {query.response.steps.map((step, index) => (
                              <div key={index} className="flex items-start space-x-2 text-sm text-gray-600">
                                <span className="flex-shrink-0 w-5 h-5 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-xs font-semibold">
                                  {index + 1}
                                </span>
                                <span>{step}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Method:</span>
                          <span className="ml-2 text-gray-600">{query.response.method}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Sources:</span>
                          <div className="mt-1">
                            {query.response.sources?.map((source, index) => (
                              <div key={index} className="text-gray-600 flex items-center">
                                <span className="w-1 h-1 bg-gray-400 rounded-full mr-2"></span>
                                {source}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default QueryHistory;