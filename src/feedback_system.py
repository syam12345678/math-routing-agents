"""Human-in-the-Loop Feedback System using DSPy for continuous learning."""

import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3
from pathlib import Path
import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate
import numpy as np

try:
    from dspy.adapters import openai as dspy_openai
except ImportError:
    dspy_openai = None

from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class FeedbackData:
    """Feedback data structure."""
    query: str
    response: Dict[str, Any]
    user_rating: int  # 1-5 scale
    user_comments: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = None
    feedback_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.feedback_id is None:
            self.feedback_id = f"fb_{int(self.timestamp.timestamp())}"


class MathTutorSignature(dspy.Signature):
    """DSPy signature for math tutoring."""
    question = dspy.InputField(desc="The math question asked by the student")
    context = dspy.InputField(desc="Additional context or previous attempts")
    solution = dspy.OutputField(desc="Step-by-step solution to the math problem")
    explanation = dspy.OutputField(desc="Clear explanation of each step")
    method = dspy.OutputField(desc="Mathematical method or approach used")


class FeedbackSignature(dspy.Signature):
    """DSPy signature for feedback analysis."""
    query = dspy.InputField(desc="The original math question")
    response = dspy.InputField(desc="The AI-generated response")
    user_rating = dspy.InputField(desc="User rating from 1-5")
    user_comments = dspy.InputField(desc="User comments or feedback")
    improvement_suggestions = dspy.OutputField(desc="Specific suggestions for improving the response")
    quality_assessment = dspy.OutputField(desc="Assessment of response quality and areas for improvement")


class MathTutorModule(dspy.Module):
    """DSPy module for math tutoring with feedback integration."""
    
    def __init__(self):
        super().__init__()
        self.generate_solution = dspy.ChainOfThought(MathTutorSignature)
        self.analyze_feedback = dspy.ChainOfThought(FeedbackSignature)
    
    def forward(self, question: str, context: str = "") -> Dict[str, str]:
        """Generate math solution with context."""
        result = self.generate_solution(question=question, context=context)
        return {
            'solution': result.solution,
            'explanation': result.explanation,
            'method': result.method
        }


class FeedbackDatabase:
    """Database for storing and managing feedback data."""
    
    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the feedback database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create feedback table
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
            
            # Create learning data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    solution TEXT NOT NULL,
                    method TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    feedback_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Feedback database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def store_feedback(self, feedback: FeedbackData) -> bool:
        """Store feedback in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback 
                (feedback_id, query, response, user_rating, user_comments, user_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.feedback_id,
                feedback.query,
                json.dumps(feedback.response),
                feedback.user_rating,
                feedback.user_comments,
                feedback.user_id,
                feedback.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored feedback {feedback.feedback_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store feedback: {str(e)}")
            return False
    
    def get_feedback_batch(self, limit: int = 100, processed: bool = False) -> List[FeedbackData]:
        """Get a batch of feedback data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT feedback_id, query, response, user_rating, user_comments, 
                       user_id, timestamp, processed
                FROM feedback 
                WHERE processed = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (processed, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            feedback_list = []
            for row in rows:
                feedback = FeedbackData(
                    feedback_id=row[0],
                    query=row[1],
                    response=json.loads(row[2]),
                    user_rating=row[3],
                    user_comments=row[4],
                    user_id=row[5],
                    timestamp=datetime.fromisoformat(row[6])
                )
                feedback_list.append(feedback)
            
            return feedback_list
            
        except Exception as e:
            logger.error(f"Failed to get feedback batch: {str(e)}")
            return []
    
    def mark_feedback_processed(self, feedback_id: str) -> bool:
        """Mark feedback as processed."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE feedback 
                SET processed = TRUE 
                WHERE feedback_id = ?
            ''', (feedback_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark feedback as processed: {str(e)}")
            return False
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total feedback count
            cursor.execute('SELECT COUNT(*) FROM feedback')
            total_feedback = cursor.fetchone()[0]
            
            # Average rating
            cursor.execute('SELECT AVG(user_rating) FROM feedback')
            avg_rating = cursor.fetchone()[0] or 0
            
            # Rating distribution
            cursor.execute('''
                SELECT user_rating, COUNT(*) 
                FROM feedback 
                GROUP BY user_rating 
                ORDER BY user_rating
            ''')
            rating_dist = dict(cursor.fetchall())
            
            # Recent feedback (last 7 days)
            cursor.execute('''
                SELECT COUNT(*) 
                FROM feedback 
                WHERE timestamp > datetime('now', '-7 days')
            ''')
            recent_feedback = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_feedback': total_feedback,
                'average_rating': round(avg_rating, 2),
                'rating_distribution': rating_dist,
                'recent_feedback': recent_feedback
            }
            
        except Exception as e:
            logger.error(f"Failed to get feedback statistics: {str(e)}")
            return {}


class FeedbackLearningSystem:
    """Main feedback learning system using DSPy."""
    
    def __init__(self):
        self.db = FeedbackDatabase()
        self.tutor_module = MathTutorModule()
        self.feedback_analyzer = dspy.ChainOfThought(FeedbackSignature)

        # Ensure DSPy-compatible OpenAI configuration
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)

        lm = None
        if dspy_openai and hasattr(dspy_openai, "Completions"):
            lm = dspy_openai.Completions(
                model=settings.llm_model,
                api_key=settings.openai_api_key,
            )
        elif hasattr(dspy, "OpenAI"):
            lm = dspy.OpenAI(
                model=settings.llm_model,
                api_key=settings.openai_api_key,
            )
        elif hasattr(dspy, "LiteLLM"):
            lm = dspy.LiteLLM(
                model=settings.llm_model,
                temperature=settings.temperature,
            )

        if lm is None:
            raise ImportError(
                "Compatible DSPy language model adapter not found. Please upgrade or downgrade dspy-ai."
            )

        dspy.settings.configure(lm=lm)
    
    async def submit_feedback(self, feedback: FeedbackData) -> bool:
        """Submit user feedback for learning."""
        try:
            # Store feedback in database
            success = self.db.store_feedback(feedback)
            
            if success:
                # Analyze feedback for immediate improvements
                await self._analyze_feedback(feedback)
                logger.info(f"Feedback submitted and analyzed: {feedback.feedback_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to submit feedback: {str(e)}")
            return False
    
    async def _analyze_feedback(self, feedback: FeedbackData) -> Dict[str, str]:
        """Analyze feedback using DSPy."""
        try:
            analysis = self.feedback_analyzer(
                query=feedback.query,
                response=json.dumps(feedback.response),
                user_rating=str(feedback.user_rating),
                user_comments=feedback.user_comments or "No comments"
            )
            
            return {
                'improvement_suggestions': analysis.improvement_suggestions,
                'quality_assessment': analysis.quality_assessment
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze feedback: {str(e)}")
            return {}
    
    async def process_feedback_batch(self, batch_size: int = 50) -> Dict[str, Any]:
        """Process a batch of feedback for learning."""
        try:
            # Get unprocessed feedback
            feedback_batch = self.db.get_feedback_batch(limit=batch_size, processed=False)
            
            if not feedback_batch:
                return {'processed': 0, 'improvements': []}
            
            improvements = []
            processed_count = 0
            
            for feedback in feedback_batch:
                try:
                    # Analyze feedback
                    analysis = await self._analyze_feedback(feedback)
                    
                    if analysis:
                        improvements.append({
                            'feedback_id': feedback.feedback_id,
                            'query': feedback.query,
                            'rating': feedback.user_rating,
                            'suggestions': analysis.get('improvement_suggestions', ''),
                            'assessment': analysis.get('quality_assessment', '')
                        })
                    
                    # Mark as processed
                    self.db.mark_feedback_processed(feedback.feedback_id)
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process feedback {feedback.feedback_id}: {str(e)}")
                    continue
            
            logger.info(f"Processed {processed_count} feedback items")
            return {
                'processed': processed_count,
                'improvements': improvements
            }
            
        except Exception as e:
            logger.error(f"Failed to process feedback batch: {str(e)}")
            return {'processed': 0, 'improvements': []}
    
    async def retrain_model(self, num_examples: int = 100) -> bool:
        """Retrain the model using feedback data."""
        try:
            # Get high-quality examples from feedback
            feedback_data = self.db.get_feedback_batch(limit=num_examples)
            
            # Filter for high-quality examples (rating >= 4)
            high_quality_feedback = [
                fb for fb in feedback_data 
                if fb.user_rating >= 4
            ]
            
            if len(high_quality_feedback) < 10:
                logger.warning("Not enough high-quality feedback for retraining")
                return False
            
            # Prepare training examples
            training_examples = []
            for feedback in high_quality_feedback[:num_examples]:
                example = dspy.Example(
                    question=feedback.query,
                    context="",
                    solution=feedback.response.get('solution', ''),
                    explanation=feedback.response.get('steps', []),
                    method=feedback.response.get('method', '')
                ).with_inputs('question', 'context')
                training_examples.append(example)
            
            # Create evaluator
            def evaluate_math_solution(example, prediction):
                # Simple evaluation based on length and structure
                solution_score = len(prediction.solution) > 50
                steps_score = len(prediction.explanation) > 2
                method_score = len(prediction.method) > 5
                return solution_score and steps_score and method_score
            
            evaluator = Evaluate(
                devset=training_examples,
                metric=evaluate_math_solution,
                num_threads=1,
                display_progress=True
            )
            
            # Bootstrap few-shot examples
            teleprompter = BootstrapFewShot(metric=evaluator, max_bootstrapped_demos=4)
            
            # Retrain the model
            optimized_tutor = teleprompter.compile(
                self.tutor_module,
                trainset=training_examples
            )
            
            # Update the module
            self.tutor_module = optimized_tutor
            
            logger.info(f"Model retrained with {len(training_examples)} examples")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retrain model: {str(e)}")
            return False
    
    async def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from feedback data."""
        try:
            stats = self.db.get_feedback_statistics()
            
            # Get recent improvements
            recent_improvements = await self.process_feedback_batch(batch_size=20)
            
            # Calculate learning trends
            insights = {
                'feedback_statistics': stats,
                'recent_improvements': recent_improvements,
                'learning_trends': self._calculate_learning_trends(),
                'recommendations': self._generate_recommendations(stats)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get learning insights: {str(e)}")
            return {}
    
    def _calculate_learning_trends(self) -> Dict[str, Any]:
        """Calculate learning trends from feedback data."""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Get daily average ratings for the last 30 days
            cursor.execute('''
                SELECT DATE(timestamp) as date, AVG(user_rating) as avg_rating
                FROM feedback 
                WHERE timestamp > datetime('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''')
            
            daily_ratings = cursor.fetchall()
            conn.close()
            
            if len(daily_ratings) < 2:
                return {'trend': 'insufficient_data'}
            
            # Calculate trend
            recent_avg = np.mean([rating for _, rating in daily_ratings[-7:]])
            older_avg = np.mean([rating for _, rating in daily_ratings[:-7]])
            
            if recent_avg > older_avg + 0.1:
                trend = 'improving'
            elif recent_avg < older_avg - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
            
            return {
                'trend': trend,
                'recent_average': round(recent_avg, 2),
                'overall_average': round(np.mean([rating for _, rating in daily_ratings]), 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate learning trends: {str(e)}")
            return {'trend': 'error'}
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on feedback statistics."""
        recommendations = []
        
        avg_rating = stats.get('average_rating', 0)
        total_feedback = stats.get('total_feedback', 0)
        
        if avg_rating < 3.0:
            recommendations.append("Consider improving solution clarity and step-by-step explanations")
        
        if avg_rating < 4.0:
            recommendations.append("Focus on mathematical accuracy and method selection")
        
        if total_feedback < 50:
            recommendations.append("Encourage more user feedback to improve learning")
        
        rating_dist = stats.get('rating_distribution', {})
        low_ratings = sum(rating_dist.get(str(i), 0) for i in range(1, 3))
        if low_ratings > total_feedback * 0.2:
            recommendations.append("Address common issues causing low ratings")
        
        return recommendations
    
    async def generate_improved_response(self, query: str, context: str = "") -> Dict[str, str]:
        """Generate an improved response using the learned model."""
        try:
            result = self.tutor_module.forward(question=query, context=context)
            return result
        except Exception as e:
            logger.error(f"Failed to generate improved response: {str(e)}")
            return {
                'solution': "I apologize, but I'm unable to generate a response at the moment.",
                'explanation': ["Error occurred"],
                'method': "Error"
            }


# Global feedback system instance
feedback_system = FeedbackLearningSystem()
