import React, { useState } from 'react';

const FeedbackInterface = ({ onSubmit, queries }) => {
  const [selectedQuery, setSelectedQuery] = useState(null);
  const [rating, setRating] = useState(5);
  const [comments, setComments] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedQuery) {
      setSubmitStatus({ type: 'error', message: 'Please select a query to provide feedback for.' });
      return;
    }

    setIsSubmitting(true);
    setSubmitStatus(null);

    const feedbackData = {
      query: selectedQuery.question,
      response: selectedQuery.response,
      user_rating: rating,
      user_comments: comments.trim() || null,
      user_id: 'user_' + Date.now()
    };

    const result = await onSubmit(feedbackData);
    
    if (result.success) {
      setSubmitStatus({ type: 'success', message: 'Thank you for your feedback! It helps improve the system.' });
      setComments('');
      setRating(5);
      setSelectedQuery(null);
    } else {
      setSubmitStatus({ type: 'error', message: result.error || 'Failed to submit feedback.' });
    }
    
    setIsSubmitting(false);
  };

  const recentQueries = queries.slice(0, 10);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
          <span className="text-3xl mr-3">💬</span>
          Provide Feedback
        </h2>
        <p className="text-gray-600 mb-8">
          Help improve the Math Routing Agent by rating solutions and providing feedback. 
          Your input helps the system learn and provide better responses.
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Query Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select a query to provide feedback for:
            </label>
            {recentQueries.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <div className="text-4xl mb-2">📝</div>
                <p className="text-gray-500">No queries available for feedback.</p>
                <p className="text-sm text-gray-400">Solve some math problems first!</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {recentQueries.map((query) => (
                  <div
                    key={query.id}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors duration-200 ${
                      selectedQuery?.id === query.id
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedQuery(query)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm text-gray-800 line-clamp-2">{query.question}</p>
                        <div className="flex items-center space-x-2 mt-1 text-xs text-gray-500">
                          <span>{new Date(query.timestamp).toLocaleDateString()}</span>
                          <span>•</span>
                          <span className={`px-2 py-0.5 rounded-full ${
                            query.routing === 'knowledge_base' 
                              ? 'bg-green-100 text-green-700' 
                              : 'bg-blue-100 text-blue-700'
                          }`}>
                            {query.routing === 'knowledge_base' ? 'Knowledge Base' : 'Web Search'}
                          </span>
                        </div>
                      </div>
                      <div className="ml-3">
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          selectedQuery?.id === query.id
                            ? 'border-indigo-500 bg-indigo-500'
                            : 'border-gray-300'
                        }`}>
                          {selectedQuery?.id === query.id && (
                            <div className="w-full h-full rounded-full bg-white scale-50"></div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Rating */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Rate the solution quality (1-5 stars):
            </label>
            <div className="flex items-center space-x-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  className={`text-2xl transition-colors duration-200 ${
                    star <= rating ? 'text-yellow-400' : 'text-gray-300'
                  }`}
                >
                  ★
                </button>
              ))}
              <span className="ml-2 text-sm text-gray-600">
                {rating === 1 && 'Poor'}
                {rating === 2 && 'Fair'}
                {rating === 3 && 'Good'}
                {rating === 4 && 'Very Good'}
                {rating === 5 && 'Excellent'}
              </span>
            </div>
          </div>

          {/* Comments */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Additional comments (optional):
            </label>
            <textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Share your thoughts about the solution, accuracy, clarity, or suggestions for improvement..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              rows={4}
            />
          </div>

          {/* Submit Status */}
          {submitStatus && (
            <div className={`p-4 rounded-lg ${
              submitStatus.type === 'success' 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-red-50 border border-red-200'
            }`}>
              <div className="flex items-center">
                <span className={`text-xl mr-2 ${
                  submitStatus.type === 'success' ? 'text-green-500' : 'text-red-500'
                }`}>
                  {submitStatus.type === 'success' ? '✅' : '⚠️'}
                </span>
                <span className={`font-medium ${
                  submitStatus.type === 'success' ? 'text-green-700' : 'text-red-700'
                }`}>
                  {submitStatus.message}
                </span>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={!selectedQuery || isSubmitting}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Submitting...</span>
                </>
              ) : (
                <>
                  <span>Submit Feedback</span>
                  <span>📤</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Feedback Benefits */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium text-blue-800 mb-2">Why provide feedback?</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Helps improve solution accuracy and clarity</li>
            <li>• Enables the system to learn from your preferences</li>
            <li>• Contributes to better routing decisions</li>
            <li>• Supports continuous system improvement</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default FeedbackInterface;