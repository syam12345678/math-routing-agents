"""FastAPI main application for Math Routing Agent."""

import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from src.config import settings
from src.guardrails import guardrails
from src.knowledge_base import knowledge_base
from src.routing_agent import routing_agent
from src.feedback_system import feedback_system, FeedbackData
from src.mcp_search import mcp_search

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for API
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Math Routing Agent...")
    
    try:
        # Initialize knowledge base
        await knowledge_base.initialize()
        logger.info("Knowledge base initialized")
        
        # Initialize other components
        logger.info("All components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Math Routing Agent...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic RAG system for mathematical problem solving with human-in-the-loop feedback",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency functions
async def get_current_user_id() -> Optional[str]:
    """Get current user ID (placeholder for authentication)."""
    # In production, implement proper authentication
    return "anonymous_user"


# API Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Math Routing Agent API",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check knowledge base
        kb_stats = await knowledge_base.get_collection_stats()
        kb_status = "healthy" if kb_stats.get('total_problems', 0) > 0 else "empty"
        
        # Check other components
        components = {
            "knowledge_base": kb_status,
            "routing_agent": "healthy",
            "feedback_system": "healthy",
            "mcp_search": "healthy"
        }
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            components=components
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            version=settings.app_version,
            components={"error": str(e)}
        )


@app.post("/query", response_model=MathQueryResponse)
async def process_math_query(
    request: MathQueryRequest,
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = Depends(get_current_user_id)
):
    """Process a math query through the routing agent."""
    try:
        logger.info(f"Processing query: {request.question[:50]}...")
        
        # Process query through routing agent
        result = await routing_agent.process_query(
            query=request.question,
            user_id=user_id or request.user_id
        )
        
        if result['success']:
            # Schedule background task for learning
            background_tasks.add_task(
                _process_query_for_learning,
                request.question,
                result['response'],
                user_id or request.user_id
            )
            
            return MathQueryResponse(
                success=True,
                response=result['response'],
                routing_decision=result.get('routing_decision'),
                confidence=result.get('confidence')
            )
        else:
            return MathQueryResponse(
                success=False,
                error=result.get('error', 'Unknown error'),
                response=None
            )
            
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for learning."""
    try:
        # Validate rating
        if not 1 <= request.user_rating <= 5:
            raise HTTPException(
                status_code=400,
                detail="User rating must be between 1 and 5"
            )
        
        # Create feedback data
        feedback = FeedbackData(
            query=request.query,
            response=request.response,
            user_rating=request.user_rating,
            user_comments=request.user_comments,
            user_id=request.user_id
        )
        
        # Submit feedback
        success = await feedback_system.submit_feedback(feedback)
        
        if success:
            return FeedbackResponse(
                success=True,
                message="Feedback submitted successfully",
                feedback_id=feedback.feedback_id
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
        insights = await feedback_system.get_learning_insights()
        return insights
        
    except Exception as e:
        logger.error(f"Failed to get feedback insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback/process")
async def process_feedback_batch(background_tasks: BackgroundTasks):
    """Process feedback batch for learning."""
    try:
        # Process feedback in background
        background_tasks.add_task(_process_feedback_batch)
        
        return {"message": "Feedback processing started"}
        
    except Exception as e:
        logger.error(f"Failed to start feedback processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback/retrain")
async def retrain_model(background_tasks: BackgroundTasks):
    """Retrain the model using feedback data."""
    try:
        # Retrain model in background
        background_tasks.add_task(_retrain_model)
        
        return {"message": "Model retraining started"}
        
    except Exception as e:
        logger.error(f"Failed to start model retraining: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    """Get knowledge base statistics."""
    try:
        stats = await knowledge_base.get_collection_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get knowledge base stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge-base/search")
async def search_knowledge_base(query: str, limit: int = 5):
    """Search the knowledge base directly."""
    try:
        results = await knowledge_base.search(query, limit=limit)
        return {"results": results}
        
    except Exception as e:
        logger.error(f"Knowledge base search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/web-search")
async def search_web(query: str, max_results: int = 5):
    """Search the web using MCP."""
    try:
        results = await mcp_search.search_and_extract_solution(query)
        return results
        
    except Exception as e:
        logger.error(f"Web search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Background task functions
async def _process_query_for_learning(query: str, response: Dict[str, Any], user_id: str):
    """Process query for learning purposes."""
    try:
        # Log query for analysis
        logger.info(f"Processing query for learning: {query[:50]}...")
        
        # You can add additional learning logic here
        # For example, updating query patterns, tracking success rates, etc.
        
    except Exception as e:
        logger.error(f"Failed to process query for learning: {str(e)}")


async def _process_feedback_batch():
    """Process feedback batch in background."""
    try:
        logger.info("Processing feedback batch...")
        result = await feedback_system.process_feedback_batch()
        logger.info(f"Processed {result['processed']} feedback items")
        
    except Exception as e:
        logger.error(f"Failed to process feedback batch: {str(e)}")


async def _retrain_model():
    """Retrain model in background."""
    try:
        logger.info("Starting model retraining...")
        success = await feedback_system.retrain_model()
        
        if success:
            logger.info("Model retraining completed successfully")
        else:
            logger.warning("Model retraining failed or insufficient data")
            
    except Exception as e:
        logger.error(f"Failed to retrain model: {str(e)}")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
