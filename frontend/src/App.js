import React, { useState, useEffect } from 'react';
import './index.css';
import Header from './components/Header';
import MathQueryInterface from './components/MathQueryInterface';
import QueryHistory from './components/QueryHistory';
import FeedbackInterface from './components/FeedbackInterface';
import AnalyticsDashboard from './components/AnalyticsDashboard';

// Use an explicit REACT_APP_API_URL to override (e.g. in production or remote testing).
// Default to empty string so calls become relative ("/query") and are proxied by
// the CRA dev server. This is important when accessing the frontend via the
// machine network IP (e.g. http://192.168.1.5:3000) where `localhost` in the
// browser would refer to the client's device instead of the server.
const API_BASE_URL = process.env.REACT_APP_API_URL ?? '';

function App() {
  const [queries, setQueries] = useState([]);
  const [feedback, setFeedback] = useState([]);
  const [systemStats, setSystemStats] = useState(null);
  const [activeTab, setActiveTab] = useState('query');
  const [isLoading, setIsLoading] = useState(false);

  // Load system statistics on component mount
  useEffect(() => {
    loadSystemStats();
  }, []);

  const loadSystemStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/knowledge-base/stats`);
      const data = await response.json();
      setSystemStats(data);
    } catch (error) {
      console.error('Failed to load system stats:', error);
    }
  };

  const handleQuerySubmit = async (question) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();
      
      if (data.success) {
        const newQuery = {
          id: Date.now(),
          question,
          response: data.response,
          timestamp: new Date().toISOString(),
          routing: data.routing_decision,
          confidence: data.confidence,
        };
        
        setQueries(prev => [newQuery, ...prev]);
        return { success: true, data: newQuery };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      console.error('Query failed:', error);
      return { success: false, error: 'Network error. Please check if the backend is running.' };
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedbackSubmit = async (feedbackData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackData),
      });

      const data = await response.json();
      
      if (data.success) {
        setFeedback(prev => [...prev, { ...feedbackData, id: data.feedback_id }]);
        return { success: true };
      } else {
        return { success: false, error: data.message };
      }
    } catch (error) {
      console.error('Feedback submission failed:', error);
      return { success: false, error: 'Failed to submit feedback' };
    }
  };

  const clearHistory = () => {
    setQueries([]);
  };

  const getTabContent = () => {
    switch (activeTab) {
      case 'query':
        return (
          <MathQueryInterface
            onSubmit={handleQuerySubmit}
            isLoading={isLoading}
            recentQueries={queries.slice(0, 3)}
          />
        );
      case 'history':
        return (
          <QueryHistory
            queries={queries}
            onClear={clearHistory}
          />
        );
      case 'feedback':
        return (
          <FeedbackInterface
            onSubmit={handleFeedbackSubmit}
            queries={queries}
          />
        );
      case 'analytics':
        return (
          <AnalyticsDashboard
            queries={queries}
            feedback={feedback}
            systemStats={systemStats}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header 
        activeTab={activeTab} 
        onTabChange={setActiveTab}
        systemStats={systemStats}
      />
      
      <main className="container mx-auto px-4 py-8">
        {getTabContent()}
      </main>
      
      <footer className="bg-white border-t border-gray-200 py-6 mt-12">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p className="text-sm">
            Math Routing Agent - Advanced AI System for Mathematical Problem Solving
          </p>
          <p className="text-xs mt-2">
            Powered by Knowledge Base Routing, Web Search, and Human-in-the-Loop Learning
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;