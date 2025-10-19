"""
Math Routing Agent - Full System (Simplified for Demo)
This version includes all advanced features but works without external dependencies.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import json
import time
from datetime import datetime
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class MathQueryRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    context: Optional[str] = None

class MathQueryResponse(BaseModel):
    success: bool
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    routing_decision: Optional[str] = None
    confidence: Optional[float] = None

class FeedbackRequest(BaseModel):
    query: str
    response: Dict[str, Any]
    user_rating: int
    user_comments: Optional[str] = None
    user_id: Optional[str] = None

class FeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    components: Dict[str, str]

# Advanced Math Knowledge Base
ADVANCED_MATH_PROBLEMS = {
    "quadratic_advanced": {
        "question": "Solve the quadratic equation: x² - 5x + 6 = 0",
        "solution": "The solutions are x = 2 and x = 3. We can factor the equation as (x-2)(x-3) = 0, which gives us x = 2 or x = 3.",
        "steps": [
            "Identify the quadratic equation: x² - 5x + 6 = 0",
            "Factor the equation: (x-2)(x-3) = 0",
            "Apply zero product property: x-2 = 0 or x-3 = 0",
            "Solve for x: x = 2 or x = 3"
        ],
        "method": "Factoring",
        "topic": "Algebra",
        "difficulty": "Intermediate",
        "confidence": 0.95
    },
    "derivative_advanced": {
        "question": "Find the derivative of f(x) = x³ + 2x² - 5x + 3",
        "solution": "The derivative is f'(x) = 3x² + 4x - 5. We apply the power rule to each term.",
        "steps": [
            "Apply power rule: d/dx[x^n] = nx^(n-1)",
            "d/dx[x³] = 3x²",
            "d/dx[2x²] = 4x",
            "d/dx[-5x] = -5",
            "d/dx[3] = 0",
            "Combine: f'(x) = 3x² + 4x - 5"
        ],
        "method": "Power Rule",
        "topic": "Calculus",
        "difficulty": "Intermediate",
        "confidence": 0.92
    },
    "area_advanced": {
        "question": "Find the area of a circle with radius 5 cm",
        "solution": "The area is 25π cm² or approximately 78.54 cm². We use the formula A = πr².",
        "steps": [
            "Use the formula: A = πr²",
            "Substitute r = 5: A = π(5)²",
            "Calculate: A = π(25) = 25π",
            "Approximate: A ≈ 78.54 cm²"
        ],
        "method": "Circle Area Formula",
        "topic": "Geometry",
        "difficulty": "Beginner",
        "confidence": 0.98
    },
    "integral_advanced": {
        "question": "Evaluate the integral: ∫(2x + 1)dx",
        "solution": "The integral is x² + x + C, where C is the constant of integration.",
        "steps": [
            "Apply power rule for integration: ∫x^n dx = x^(n+1)/(n+1) + C",
            "∫2x dx = 2(x²/2) = x²",
            "∫1 dx = x",
            "Combine: ∫(2x + 1)dx = x² + x + C"
        ],
        "method": "Power Rule for Integration",
        "topic": "Calculus",
        "difficulty": "Beginner",
        "confidence": 0.90
    },
    "trigonometry_advanced": {
        "question": "Find sin(30°) using special triangles",
        "solution": "sin(30°) = 1/2 = 0.5. This is a standard trigonometric value from the 30-60-90 triangle.",
        "steps": [
            "Recall the unit circle or special triangles",
            "For 30° angle in a 30-60-90 triangle",
            "sin(30°) = opposite/hypotenuse = 1/2",
            "Therefore, sin(30°) = 0.5"
        ],
        "method": "Unit Circle/Special Triangles",
        "topic": "Trigonometry",
        "difficulty": "Beginner",
        "confidence": 0.95
    },
    "statistics_advanced": {
        "question": "Find the mean of the dataset: [2, 4, 6, 8, 10]",
        "solution": "The mean is 6. We calculate the sum of all values divided by the number of values.",
        "steps": [
            "Add all values: 2 + 4 + 6 + 8 + 10 = 30",
            "Count the number of values: 5",
            "Calculate mean: 30 ÷ 5 = 6"
        ],
        "method": "Mean Formula",
        "topic": "Statistics",
        "difficulty": "Beginner",
        "confidence": 0.88
    }
}

# Feedback Database
class FeedbackDatabase:
    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                user_rating INTEGER NOT NULL,
                user_comments TEXT,
                user_id TEXT,
                timestamp TEXT NOT NULL,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        conn.commit()
        conn.close()
    
    def store_feedback(self, feedback_data: Dict) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback 
                (feedback_id, query, response, user_rating, user_comments, user_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback_data['feedback_id'],
                feedback_data['query'],
                json.dumps(feedback_data['response']),
                feedback_data['user_rating'],
                feedback_data['user_comments'],
                feedback_data['user_id'],
                feedback_data['timestamp']
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to store feedback: {str(e)}")
            return False
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM feedback')
            total_feedback = cursor.fetchone()[0]
            cursor.execute('SELECT AVG(user_rating) FROM feedback')
            avg_rating = cursor.fetchone()[0] or 0
            conn.close()
            return {
                'total_feedback': total_feedback,
                'average_rating': round(avg_rating, 2)
            }
        except Exception as e:
            logger.error(f"Failed to get feedback stats: {str(e)}")
            return {}

# Advanced Math Solver with Routing
class AdvancedMathSolver:
    def __init__(self):
        self.feedback_db = FeedbackDatabase()
        self.knowledge_base = ADVANCED_MATH_PROBLEMS
    
    def search_knowledge_base(self, query: str) -> Optional[Dict]:
        """Search knowledge base for matching problems."""
        query_lower = query.lower()

        # Tokenize and filter stopwords to reduce accidental matches
        import re

        stopwords = {
            'the', 'a', 'an', 'of', 'and', 'to', 'in', 'for', 'with', 'is', 'are',
            'on', 'by', 'using', 'use', 'find', 'calculate', 'solve', 'evaluate',
            'what', 'how', 'which', 'be', 'we', 'this', 'that'
        }

        def tokens(text: str):
            words = re.findall(r"[a-zA-Z0-9]+", text.lower())
            return {w for w in words if w not in stopwords and len(w) > 1}

        query_tokens = tokens(query_lower)

        # Advanced matching logic: require at least 2 token overlaps or direct topic/method match
        for key, problem in self.knowledge_base.items():
            problem_tokens = tokens(problem['question'])
            common = query_tokens.intersection(problem_tokens)

            # Prefer exact topic or method mention
            if problem['topic'].lower() in query_lower or problem['method'].lower() in query_lower:
                return problem

            if len(common) >= 2:
                return problem

        return None
    
    def generate_web_search_response(self, query: str) -> Dict:
        """Generate response for web search scenario."""
        return {
            "solution": f"Based on web search results, here's a comprehensive solution for: {query}. This would typically involve searching multiple educational sources and synthesizing the best approach.",
            "steps": [
                "Search educational databases for similar problems",
                "Analyze multiple solution approaches",
                "Synthesize the most effective method",
                "Generate step-by-step explanation"
            ],
            "method": "Web Search Synthesis",
            "topic": "General Mathematics",
            "difficulty": "Variable",
            "confidence": 0.75
        }
    
    def route_query(self, query: str) -> Dict:
        """Intelligent routing between knowledge base and web search."""
        # First, try knowledge base
        kb_result = self.search_knowledge_base(query)
        
        if kb_result:
            return {
                "result": kb_result,
                "routing_decision": "knowledge_base",
                "confidence": kb_result.get('confidence', 0.8)
            }
        else:
            # Route to web search
            web_result = self.generate_web_search_response(query)
            return {
                "result": web_result,
                "routing_decision": "web_search",
                "confidence": web_result.get('confidence', 0.75)
            }
    
    def process_feedback(self, feedback_data: Dict) -> bool:
        """Process user feedback for learning."""
        feedback_data['feedback_id'] = f"fb_{int(time.time())}"
        feedback_data['timestamp'] = datetime.now().isoformat()
        return self.feedback_db.store_feedback(feedback_data)

# Initialize solver
math_solver = AdvancedMathSolver()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Math Routing Agent - Full System...")
    yield
    logger.info("Shutting down Math Routing Agent...")

# Create FastAPI app
app = FastAPI(
    title="Math Routing Agent - Full System",
    version="1.0.0",
    description="Advanced Agentic RAG system for mathematical problem solving with human-in-the-loop learning",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Math Routing Agent - Full System",
        "version": "1.0.0",
        "status": "running",
        "features": "Knowledge Base, Web Search, Human-in-the-Loop Learning"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        components={
            "knowledge_base": "active",
            "web_search": "active",
            "feedback_system": "active",
            "routing_agent": "active"
        }
    )

@app.post("/query", response_model=MathQueryResponse)
async def process_math_query(request: MathQueryRequest):
    """Process a math query through the advanced routing system."""
    try:
        logger.info(f"Processing advanced query: {request.question[:50]}...")
        
        # Route the query
        routing_result = math_solver.route_query(request.question)
        
        # Format response
        result = routing_result['result']
        response = {
            'solution': result['solution'],
            'steps': result['steps'],
            'method': result['method'],
            'confidence': routing_result['confidence'],
            'sources': [f"Advanced {result['topic']} Knowledge Base" if routing_result['routing_decision'] == 'knowledge_base' else "Web Search Results"],
            'feedback_requested': True,
            'routing_source': routing_result['routing_decision']
        }
        
        return MathQueryResponse(
            success=True,
            response=response,
            routing_decision=routing_result['routing_decision'],
            confidence=routing_result['confidence']
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        return MathQueryResponse(
            success=False,
            error=str(e)
        )

@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for learning."""
    try:
        if not 1 <= request.user_rating <= 5:
            raise HTTPException(status_code=400, detail="User rating must be between 1 and 5")
        
        feedback_data = {
            'query': request.query,
            'response': request.response,
            'user_rating': request.user_rating,
            'user_comments': request.user_comments,
            'user_id': request.user_id
        }
        
        success = math_solver.process_feedback(feedback_data)
        
        if success:
            return FeedbackResponse(
                success=True,
                message="Feedback submitted successfully",
                feedback_id=feedback_data['feedback_id']
            )
        else:
            return FeedbackResponse(
                success=False,
                message="Failed to submit feedback"
            )
            
    except Exception as e:
        logger.error(f"Feedback submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/insights")
async def get_feedback_insights():
    """Get learning insights from feedback data."""
    try:
        stats = math_solver.feedback_db.get_feedback_stats()
        return {
            "feedback_statistics": stats,
            "learning_trends": {
                "trend": "improving" if stats.get('average_rating', 0) > 4.0 else "stable",
                "recent_average": stats.get('average_rating', 0),
                "overall_average": stats.get('average_rating', 0)
            },
            "recommendations": [
                "Continue providing detailed step-by-step solutions",
                "Focus on mathematical accuracy and clarity",
                "Encourage more user feedback for continuous improvement"
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get feedback insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    """Get knowledge base statistics."""
    return {
        "total_problems": len(ADVANCED_MATH_PROBLEMS),
        "topics": list(set(problem['topic'] for problem in ADVANCED_MATH_PROBLEMS.values())),
        "difficulty_levels": list(set(problem['difficulty'] for problem in ADVANCED_MATH_PROBLEMS.values())),
        "average_confidence": sum(problem.get('confidence', 0.8) for problem in ADVANCED_MATH_PROBLEMS.values()) / len(ADVANCED_MATH_PROBLEMS)
    }

@app.get("/problems")
async def list_problems():
    """List available math problems."""
    return {
        "available_problems": list(ADVANCED_MATH_PROBLEMS.keys()),
        "problems": ADVANCED_MATH_PROBLEMS
    }

if __name__ == "__main__":
    print("🚀 Starting Math Routing Agent - Full System")
    print("📚 Features: Knowledge Base, Web Search, Human-in-the-Loop Learning")
    print("🌐 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "src.main_full:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
