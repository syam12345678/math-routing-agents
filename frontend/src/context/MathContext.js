import React, { createContext, useContext, useReducer, useEffect } from 'react';
import axios from 'axios';

const MathContext = createContext();

// API base URL: prefer REACT_APP_API_URL (for production). Default to '' so
// requests are relative and will be proxied by the CRA dev server during
// development. This avoids issues when accessing the app via a network IP.
const API_BASE_URL = process.env.REACT_APP_API_URL ?? '';

// Action types
const ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  SET_QUERY: 'SET_QUERY',
  SET_RESPONSE: 'SET_RESPONSE',
  SET_ERROR: 'SET_ERROR',
  ADD_QUERY_HISTORY: 'ADD_QUERY_HISTORY',
  SET_FEEDBACK: 'SET_FEEDBACK',
  SET_ANALYTICS: 'SET_ANALYTICS',
  CLEAR_RESPONSE: 'CLEAR_RESPONSE'
};

// Initial state
const initialState = {
  isLoading: false,
  currentQuery: '',
  currentResponse: null,
  error: null,
  queryHistory: [],
  feedback: null,
  analytics: null
};

// Reducer
function mathReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_LOADING:
      return { ...state, isLoading: action.payload };
    
    case ACTIONS.SET_QUERY:
      return { ...state, currentQuery: action.payload };
    
    case ACTIONS.SET_RESPONSE:
      return { 
        ...state, 
        currentResponse: action.payload,
        error: null,
        isLoading: false
      };
    
    case ACTIONS.SET_ERROR:
      return { 
        ...state, 
        error: action.payload,
        isLoading: false
      };
    
    case ACTIONS.ADD_QUERY_HISTORY:
      return {
        ...state,
        queryHistory: [action.payload, ...state.queryHistory.slice(0, 9)] // Keep last 10
      };
    
    case ACTIONS.SET_FEEDBACK:
      return { ...state, feedback: action.payload };
    
    case ACTIONS.SET_ANALYTICS:
      return { ...state, analytics: action.payload };
    
    case ACTIONS.CLEAR_RESPONSE:
      return { 
        ...state, 
        currentResponse: null,
        error: null
      };
    
    default:
      return state;
  }
}

// Provider component
export function MathProvider({ children }) {
  const [state, dispatch] = useReducer(mathReducer, initialState);

  // API functions
  const submitQuery = async (query, userId = null) => {
    dispatch({ type: ACTIONS.SET_LOADING, payload: true });
    dispatch({ type: ACTIONS.SET_QUERY, payload: query });
    
    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        question: query,
        user_id: userId
      });
      
      if (response.data.success) {
        dispatch({ type: ACTIONS.SET_RESPONSE, payload: response.data });
        dispatch({ 
          type: ACTIONS.ADD_QUERY_HISTORY, 
          payload: {
            query,
            response: response.data,
            timestamp: new Date().toISOString()
          }
        });
      } else {
        dispatch({ type: ACTIONS.SET_ERROR, payload: response.data.error });
      }
    } catch (error) {
      dispatch({ 
        type: ACTIONS.SET_ERROR, 
        payload: error.response?.data?.error || 'Failed to process query'
      });
    }
  };

  const submitFeedback = async (feedbackData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/feedback`, feedbackData);
      
      if (response.data.success) {
        dispatch({ type: ACTIONS.SET_FEEDBACK, payload: response.data });
        return response.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to submit feedback');
    }
  };

  const getAnalytics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/feedback/insights`);
      dispatch({ type: ACTIONS.SET_ANALYTICS, payload: response.data });
      return response.data;
    } catch (error) {
      console.error('Failed to get analytics:', error);
      return null;
    }
  };

  const searchKnowledgeBase = async (query, limit = 5) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/knowledge-base/search`, {
        query,
        limit
      });
      return response.data.results;
    } catch (error) {
      console.error('Knowledge base search failed:', error);
      return [];
    }
  };

  const searchWeb = async (query, maxResults = 5) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/web-search`, {
        query,
        max_results: maxResults
      });
      return response.data;
    } catch (error) {
      console.error('Web search failed:', error);
      return null;
    }
  };

  const clearResponse = () => {
    dispatch({ type: ACTIONS.CLEAR_RESPONSE });
  };

  // Load analytics on mount
  useEffect(() => {
    getAnalytics();
  }, []);

  const value = {
    ...state,
    submitQuery,
    submitFeedback,
    getAnalytics,
    searchKnowledgeBase,
    searchWeb,
    clearResponse
  };

  return (
    <MathContext.Provider value={value}>
      {children}
    </MathContext.Provider>
  );
}

// Custom hook
export function useMath() {
  const context = useContext(MathContext);
  if (!context) {
    throw new Error('useMath must be used within a MathProvider');
  }
  return context;
}

export default MathContext;
