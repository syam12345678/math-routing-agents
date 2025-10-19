import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const AnalyticsDashboard = ({ queries, feedback, systemStats }) => {
  const [feedbackInsights, setFeedbackInsights] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadFeedbackInsights();
  }, []);

  const loadFeedbackInsights = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/feedback/insights`);
      const data = await response.json();
      setFeedbackInsights(data);
    } catch (error) {
      console.error('Failed to load feedback insights:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate query statistics
  const queryStats = {
    total: queries.length,
    knowledgeBase: queries.filter(q => q.routing === 'knowledge_base').length,
    webSearch: queries.filter(q => q.routing === 'web_search').length,
    averageConfidence: queries.length > 0 
      ? queries.reduce((sum, q) => sum + q.confidence, 0) / queries.length 
      : 0,
    recentQueries: queries.filter(q => {
      const queryDate = new Date(q.timestamp);
      const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      return queryDate > oneDayAgo;
    }).length
  };

  // Calculate routing efficiency
  const routingEfficiency = {
    knowledgeBaseAccuracy: queryStats.knowledgeBase > 0 
      ? queries.filter(q => q.routing === 'knowledge_base').reduce((sum, q) => sum + q.confidence, 0) / queryStats.knowledgeBase
      : 0,
    webSearchAccuracy: queryStats.webSearch > 0
      ? queries.filter(q => q.routing === 'web_search').reduce((sum, q) => sum + q.confidence, 0) / queryStats.webSearch
      : 0
  };

  const StatCard = ({ title, value, subtitle, icon, color = 'indigo' }) => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg bg-${color}-100`}>
          <span className="text-2xl">{icon}</span>
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
        </div>
      </div>
    </div>
  );

  const ProgressBar = ({ label, value, max = 1, color = 'indigo' }) => (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{Math.round(value * 100)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`bg-${color}-500 h-2 rounded-full transition-all duration-300`}
          style={{ width: `${Math.min((value / max) * 100, 100)}%` }}
        ></div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2 flex items-center">
          <span className="text-3xl mr-3">📊</span>
          Analytics Dashboard
        </h2>
        <p className="text-gray-600">
          Monitor system performance, user engagement, and learning progress.
        </p>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Queries"
          value={queryStats.total}
          subtitle="All time"
          icon="🧮"
          color="blue"
        />
        <StatCard
          title="Knowledge Base"
          value={queryStats.knowledgeBase}
          subtitle={`${queryStats.total > 0 ? Math.round((queryStats.knowledgeBase / queryStats.total) * 100) : 0}% of queries`}
          icon="📚"
          color="green"
        />
        <StatCard
          title="Web Search"
          value={queryStats.webSearch}
          subtitle={`${queryStats.total > 0 ? Math.round((queryStats.webSearch / queryStats.total) * 100) : 0}% of queries`}
          icon="🌐"
          color="purple"
        />
        <StatCard
          title="Avg Confidence"
          value={`${Math.round(queryStats.averageConfidence * 100)}%`}
          subtitle="Solution accuracy"
          icon="🎯"
          color="orange"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Query Performance */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <span className="text-xl mr-2">⚡</span>
            Query Performance
          </h3>
          <div className="space-y-4">
            <ProgressBar
              label="Knowledge Base Accuracy"
              value={routingEfficiency.knowledgeBaseAccuracy}
              color="green"
            />
            <ProgressBar
              label="Web Search Accuracy"
              value={routingEfficiency.webSearchAccuracy}
              color="purple"
            />
            <ProgressBar
              label="Overall System Confidence"
              value={queryStats.averageConfidence}
              color="blue"
            />
          </div>
        </div>

        {/* System Statistics */}
        {systemStats && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="text-xl mr-2">🔧</span>
              System Statistics
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Available Problems</span>
                <span className="font-semibold text-gray-800">{systemStats.total_problems}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Topics Covered</span>
                <span className="font-semibold text-gray-800">{systemStats.topics?.length || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Difficulty Levels</span>
                <span className="font-semibold text-gray-800">{systemStats.difficulty_levels?.length || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Avg Knowledge Confidence</span>
                <span className="font-semibold text-gray-800">
                  {Math.round((systemStats.average_confidence || 0) * 100)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Feedback Insights */}
        {feedbackInsights && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="text-xl mr-2">💬</span>
              Feedback Insights
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Feedback</span>
                <span className="font-semibold text-gray-800">
                  {feedbackInsights.feedback_statistics?.total_feedback || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Average Rating</span>
                <span className="font-semibold text-gray-800">
                  {feedbackInsights.feedback_statistics?.average_rating || 0}/5
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Learning Trend</span>
                <span className={`font-semibold ${
                  feedbackInsights.learning_trends?.trend === 'improving' 
                    ? 'text-green-600' 
                    : 'text-yellow-600'
                }`}>
                  {feedbackInsights.learning_trends?.trend || 'Stable'}
                </span>
              </div>
            </div>
            
            {feedbackInsights.recommendations && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Recommendations:</h4>
                <ul className="text-xs text-gray-600 space-y-1">
                  {feedbackInsights.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start">
                      <span className="w-1 h-1 bg-indigo-500 rounded-full mr-2 mt-2 flex-shrink-0"></span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <span className="text-xl mr-2">🕒</span>
            Recent Activity
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Queries Today</span>
              <span className="font-semibold text-gray-800">{queryStats.recentQueries}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Feedback</span>
              <span className="font-semibold text-gray-800">{feedback.length}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">System Uptime</span>
              <span className="font-semibold text-green-600">Online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Refresh Button */}
      <div className="flex justify-center">
        <button
          onClick={loadFeedbackInsights}
          disabled={isLoading}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center space-x-2"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Loading...</span>
            </>
          ) : (
            <>
              <span>Refresh Data</span>
              <span>🔄</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;