# Math Routing Agent - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API uses basic authentication. Include your API key in the request headers:
```http
Authorization: Bearer your_api_key_here
```

## Endpoints

### 1. Health Check

**GET** `/health`

Check the health status of the system and its components.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "knowledge_base": "healthy",
    "routing_agent": "healthy",
    "feedback_system": "healthy",
    "mcp_search": "healthy"
  }
}
```

### 2. Process Math Query

**POST** `/query`

Process a mathematical question through the routing agent.

**Request Body:**
```json
{
  "question": "Solve the quadratic equation: x² - 5x + 6 = 0",
  "user_id": "user123",
  "context": "Optional context for the question"
}
```

**Response:**
```json
{
  "success": true,
  "response": {
    "solution": "The solutions are x = 2 and x = 3...",
    "steps": [
      "Identify the quadratic equation: x² - 5x + 6 = 0",
      "Factor the equation: (x-2)(x-3) = 0",
      "Apply zero product property: x-2 = 0 or x-3 = 0",
      "Solve for x: x = 2 or x = 3"
    ],
    "method": "Factoring",
    "confidence": 0.95,
    "sources": ["Knowledge Base - Algebra"],
    "feedback_requested": true,
    "routing_source": "knowledge_base"
  },
  "routing_decision": "knowledge_base",
  "confidence": 0.95
}
```

### 3. Submit Feedback

**POST** `/feedback`

Submit user feedback for learning and improvement.

**Request Body:**
```json
{
  "query": "Solve the quadratic equation: x² - 5x + 6 = 0",
  "response": {
    "solution": "The solutions are x = 2 and x = 3...",
    "steps": ["Step 1", "Step 2", "Step 3"],
    "method": "Factoring"
  },
  "user_rating": 5,
  "user_comments": "Great explanation! Very clear steps.",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback submitted successfully",
  "feedback_id": "fb_1703123456"
}
```

### 4. Get Feedback Insights

**GET** `/feedback/insights`

Retrieve learning insights and analytics from feedback data.

**Response:**
```json
{
  "feedback_statistics": {
    "total_feedback": 150,
    "average_rating": 4.2,
    "rating_distribution": {
      "5": 45,
      "4": 60,
      "3": 30,
      "2": 10,
      "1": 5
    },
    "recent_feedback": 25
  },
  "learning_trends": {
    "trend": "improving",
    "recent_average": 4.3,
    "overall_average": 4.2
  },
  "recommendations": [
    "Consider improving solution clarity and step-by-step explanations",
    "Focus on mathematical accuracy and method selection"
  ]
}
```

### 5. Process Feedback Batch

**POST** `/feedback/process`

Process a batch of feedback for learning (background task).

**Response:**
```json
{
  "message": "Feedback processing started"
}
```

### 6. Retrain Model

**POST** `/feedback/retrain`

Retrain the model using feedback data (background task).

**Response:**
```json
{
  "message": "Model retraining started"
}
```

### 7. Get Knowledge Base Statistics

**GET** `/knowledge-base/stats`

Get statistics about the knowledge base.

**Response:**
```json
{
  "total_problems": 100,
  "vector_dimension": 384,
  "distance_metric": "Cosine"
}
```

### 8. Search Knowledge Base

**POST** `/knowledge-base/search`

Search the knowledge base directly.

**Request Body:**
```json
{
  "query": "quadratic equations",
  "limit": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "question": "Solve the quadratic equation: x² - 5x + 6 = 0",
      "solution": "The solutions are x = 2 and x = 3...",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "method": "Factoring",
      "topic": "Algebra",
      "difficulty": "Intermediate",
      "similarity_score": 0.95
    }
  ]
}
```

### 9. Web Search

**POST** `/web-search`

Search the web using MCP for math content.

**Request Body:**
```json
{
  "query": "advanced calculus integration techniques",
  "max_results": 5
}
```

**Response:**
```json
{
  "success": true,
  "solutions": [
    {
      "title": "Advanced Integration Techniques",
      "url": "https://example.com/integration",
      "content": "Integration techniques include...",
      "relevance_score": 0.85
    }
  ],
  "sources": [
    {
      "title": "Advanced Integration Techniques",
      "url": "https://example.com/integration"
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid request format",
  "status_code": 400
}
```

### 422 Validation Error
```json
{
  "success": false,
  "error": "Validation failed: Question must be at least 3 characters long",
  "status_code": 422
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error",
  "status_code": 500
}
```

## Rate Limiting

- **Query Endpoint**: 100 requests per minute per user
- **Feedback Endpoint**: 50 requests per minute per user
- **Search Endpoints**: 200 requests per minute per user

## WebSocket Support

### Real-time Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Update:', data);
};
```

## SDK Examples

### Python
```python
import requests

class MathRoutingAgent:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def query(self, question, user_id=None):
        response = requests.post(f"{self.base_url}/query", json={
            "question": question,
            "user_id": user_id
        })
        return response.json()
    
    def submit_feedback(self, query, response, rating, comments=None):
        return requests.post(f"{self.base_url}/feedback", json={
            "query": query,
            "response": response,
            "user_rating": rating,
            "user_comments": comments
        }).json()

# Usage
agent = MathRoutingAgent()
result = agent.query("Solve x² - 5x + 6 = 0")
print(result)
```

### JavaScript
```javascript
class MathRoutingAgent {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async query(question, userId = null) {
        const response = await fetch(`${this.baseUrl}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                user_id: userId
            })
        });
        return await response.json();
    }
    
    async submitFeedback(query, response, rating, comments = null) {
        const res = await fetch(`${this.baseUrl}/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                response: response,
                user_rating: rating,
                user_comments: comments
            })
        });
        return await res.json();
    }
}

// Usage
const agent = new MathRoutingAgent();
agent.query("Solve x² - 5x + 6 = 0").then(result => {
    console.log(result);
});
```

## Testing

### Using curl
```bash
# Health check
curl -X GET http://localhost:8000/health

# Submit query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Solve x² - 5x + 6 = 0"}'

# Submit feedback
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"query": "Solve x² - 5x + 6 = 0", "response": {"solution": "x = 2, x = 3"}, "user_rating": 5}'
```

### Using Postman
1. Import the API collection
2. Set the base URL to `http://localhost:8000`
3. Run the requests in sequence

## Changelog

### Version 1.0.0
- Initial release
- Basic query processing
- Feedback system
- Knowledge base integration
- Web search capabilities
- Analytics dashboard
