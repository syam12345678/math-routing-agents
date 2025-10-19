"""AI Gateway Guardrails for Input/Output Validation."""

import re
import logging
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, validator
import openai
from src.config import settings

logger = logging.getLogger(__name__)


class InputValidationError(Exception):
    """Raised when input validation fails."""
    pass


class OutputValidationError(Exception):
    """Raised when output validation fails."""
    pass


class MathQuery(BaseModel):
    """Validated math query input."""
    
    question: str
    user_id: Optional[str] = None
    context: Optional[str] = None
    
    @validator('question')
    def validate_question(cls, v):
        """Validate the math question input."""
        if not v or len(v.strip()) < 3:
            raise ValueError("Question must be at least 3 characters long")
        
        if len(v) > 1000:
            raise ValueError("Question must be less than 1000 characters")
        
        # Check for potentially harmful content
        harmful_patterns = [
            r'(?i)(hack|exploit|malware|virus)',
            r'(?i)(personal|private|confidential)',
            r'(?i)(password|credit.?card|ssn)',
            r'(?i)(illegal|unethical|harmful)'
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, v):
                raise ValueError("Question contains potentially harmful content")
        
        # Ensure it's math-related
        math_indicators = [
            'solve', 'calculate', 'find', 'prove', 'derive', 'integrate',
            'differentiate', 'equation', 'function', 'theorem', 'formula',
            'algebra', 'calculus', 'geometry', 'trigonometry', 'statistics',
            'probability', 'matrix', 'vector', 'limit', 'derivative',
            'integral', 'sum', 'product', 'logarithm', 'exponential'
        ]
        
        question_lower = v.lower()
        if not any(indicator in question_lower for indicator in math_indicators):
            logger.warning(f"Question may not be math-related: {v[:50]}...")
        
        return v.strip()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validate user ID format."""
        if v and not re.match(r'^[a-zA-Z0-9_-]{3,50}$', v):
            raise ValueError("Invalid user ID format")
        return v


class MathResponse(BaseModel):
    """Validated math response output."""
    
    solution: str
    steps: List[str]
    method: str
    confidence: float
    sources: List[str]
    feedback_requested: bool = True
    
    @validator('solution')
    def validate_solution(cls, v):
        """Validate the solution content."""
        if not v or len(v.strip()) < 10:
            raise ValueError("Solution must be at least 10 characters long")
        
        if len(v) > 5000:
            raise ValueError("Solution must be less than 5000 characters")
        
        # Check for inappropriate content
        inappropriate_patterns = [
            r'(?i)(hate|discrimination|violence)',
            r'(?i)(inappropriate|offensive)',
            r'(?i)(illegal|unethical)'
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, v):
                raise ValueError("Solution contains inappropriate content")
        
        return v.strip()
    
    @validator('steps')
    def validate_steps(cls, v):
        """Validate solution steps."""
        if not v or len(v) < 1:
            raise ValueError("At least one step is required")
        
        if len(v) > 20:
            raise ValueError("Too many steps (max 20)")
        
        for i, step in enumerate(v):
            if not step or len(step.strip()) < 5:
                raise ValueError(f"Step {i+1} must be at least 5 characters long")
        
        return v
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Validate confidence score."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class Guardrails:
    """AI Gateway Guardrails for input/output validation."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def validate_input(self, query: str, user_id: Optional[str] = None) -> MathQuery:
        """Validate input query using multiple layers of validation."""
        try:
            # Basic validation
            math_query = MathQuery(question=query, user_id=user_id)
            
            # AI-powered content validation
            await self._ai_content_validation(query)
            
            # Privacy check
            await self._privacy_validation(query)
            
            logger.info(f"Input validation passed for user {user_id}")
            return math_query
            
        except Exception as e:
            logger.error(f"Input validation failed: {str(e)}")
            raise InputValidationError(f"Input validation failed: {str(e)}")
    
    async def validate_output(self, response_data: Dict) -> MathResponse:
        """Validate output response using multiple layers of validation."""
        try:
            # Basic validation
            math_response = MathResponse(**response_data)
            
            # AI-powered content validation
            await self._ai_response_validation(response_data['solution'])
            
            # Educational quality check
            await self._educational_quality_check(response_data)
            
            logger.info("Output validation passed")
            return math_response
            
        except Exception as e:
            logger.error(f"Output validation failed: {str(e)}")
            raise OutputValidationError(f"Output validation failed: {str(e)}")
    
    async def _ai_content_validation(self, content: str) -> None:
        """Use AI to validate content appropriateness."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a content validator. Check if the input is appropriate for an educational math platform. Respond with 'APPROVED' or 'REJECTED' followed by a brief reason."
                    },
                    {
                        "role": "user",
                        "content": f"Validate this math question: {content}"
                    }
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            if not result.startswith("APPROVED"):
                raise ValueError(f"AI content validation failed: {result}")
                
        except Exception as e:
            logger.warning(f"AI content validation error: {str(e)}")
            # Don't fail the entire validation if AI check fails
    
    async def _privacy_validation(self, content: str) -> None:
        """Check for potential privacy violations."""
        privacy_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
        ]
        
        for pattern in privacy_patterns:
            if re.search(pattern, content):
                raise ValueError("Content contains potential personal information")
    
    async def _ai_response_validation(self, solution: str) -> None:
        """Use AI to validate response quality."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a math education validator. Check if the solution is mathematically correct and educationally appropriate. Respond with 'APPROVED' or 'REJECTED' followed by a brief reason."
                    },
                    {
                        "role": "user",
                        "content": f"Validate this math solution: {solution}"
                    }
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            if not result.startswith("APPROVED"):
                raise ValueError(f"AI response validation failed: {result}")
                
        except Exception as e:
            logger.warning(f"AI response validation error: {str(e)}")
    
    async def _educational_quality_check(self, response_data: Dict) -> None:
        """Check educational quality of the response."""
        solution = response_data['solution']
        steps = response_data['steps']
        
        # Check if solution has educational value
        if len(solution) < 50:
            raise ValueError("Solution too brief for educational purposes")
        
        # Check if steps are properly explained
        for step in steps:
            if len(step) < 10:
                raise ValueError("Steps must be properly explained")
        
        # Check for mathematical notation
        math_notation = re.findall(r'[+\-*/=<>()\[\]{}^]', solution)
        if len(math_notation) < 3:
            logger.warning("Solution may lack sufficient mathematical notation")


# Global guardrails instance
guardrails = Guardrails()
