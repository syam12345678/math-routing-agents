import React from 'react';

const Header = ({ activeTab, onTabChange, systemStats }) => {
  const tabs = [
    { id: 'query', label: 'Math Solver', icon: '🧮' },
    { id: 'history', label: 'History', icon: '📚' },
    { id: 'feedback', label: 'Feedback', icon: '💬' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
  ];

  return (
    <header className="bg-white shadow-lg border-b-4 border-indigo-500">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center space-x-4 mb-4 lg:mb-0">
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-3 rounded-xl shadow-lg">
              <span className="text-2xl font-bold">Math AI</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Math Routing Agent</h1>
              <p className="text-sm text-gray-600">Advanced AI System for Mathematical Problem Solving</p>
            </div>
          </div>
          
          {systemStats && (
            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>System Online</span>
              </div>
              <div className="hidden sm:block">
                <span className="font-medium">{systemStats.total_problems}</span> Problems Available
              </div>
              <div className="hidden sm:block">
                <span className="font-medium">{systemStats.topics?.length || 0}</span> Topics
              </div>
            </div>
          )}
        </div>
        
        <nav className="mt-6">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                }`}
              >
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </nav>
      </div>
    </header>
  );
};

export default Header;