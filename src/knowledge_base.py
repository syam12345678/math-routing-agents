"""Knowledge Base for Math Routing Agent using Qdrant Vector Database."""

import json
import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)


class MathKnowledgeBase:
    """Math Knowledge Base using Qdrant Vector Database."""
    
    def __init__(self):
        self.client = QdrantClient(
            url="http://localhost:6333",
            api_key=None  # Add API key if needed
        )
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.collection_name = "math_knowledge"
        self.vector_dimension = 384
        
    async def initialize(self):
        """Initialize the knowledge base and create collection if needed."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
            
            # Load math dataset if collection is empty
            collection_info = self.client.get_collection(self.collection_name)
            if collection_info.points_count == 0:
                await self._load_math_dataset()
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {str(e)}")
            raise
    
    async def _load_math_dataset(self):
        """Load comprehensive math dataset into the vector database."""
        logger.info("Loading math dataset...")
        
        # Create comprehensive math dataset
        math_data = self._create_math_dataset()
        
        # Process and embed the data
        points = []
        for i, item in enumerate(math_data):
            # Generate embedding
            embedding = self.embedding_model.encode(item['content']).tolist()
            
            # Create point
            point = PointStruct(
                id=i,
                vector=embedding,
                payload={
                    'question': item['question'],
                    'solution': item['solution'],
                    'steps': item['steps'],
                    'method': item['method'],
                    'topic': item['topic'],
                    'difficulty': item['difficulty'],
                    'content': item['content']
                }
            )
            points.append(point)
        
        # Upload points in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        logger.info(f"Loaded {len(math_data)} math problems into knowledge base")
    
    def _create_math_dataset(self) -> List[Dict]:
        """Create a comprehensive math dataset covering various topics."""
        math_data = []
        
        # Algebra Problems
        algebra_problems = [
            {
                'question': 'Solve the quadratic equation: x² - 5x + 6 = 0',
                'solution': 'The solutions are x = 2 and x = 3. We can factor the equation as (x-2)(x-3) = 0, which gives us x = 2 or x = 3.',
                'steps': [
                    'Identify the quadratic equation: x² - 5x + 6 = 0',
                    'Factor the equation: (x-2)(x-3) = 0',
                    'Apply zero product property: x-2 = 0 or x-3 = 0',
                    'Solve for x: x = 2 or x = 3'
                ],
                'method': 'Factoring',
                'topic': 'Algebra',
                'difficulty': 'Intermediate',
                'content': 'quadratic equation solving factoring x² - 5x + 6 = 0 solutions x = 2 x = 3'
            },
            {
                'question': 'Simplify the expression: (2x + 3)(x - 4)',
                'solution': 'The simplified form is 2x² - 5x - 12. We use the FOIL method to expand the expression.',
                'steps': [
                    'Apply FOIL method: First, Outer, Inner, Last',
                    'First: 2x × x = 2x²',
                    'Outer: 2x × (-4) = -8x',
                    'Inner: 3 × x = 3x',
                    'Last: 3 × (-4) = -12',
                    'Combine like terms: 2x² - 8x + 3x - 12 = 2x² - 5x - 12'
                ],
                'method': 'FOIL Method',
                'topic': 'Algebra',
                'difficulty': 'Beginner',
                'content': 'simplify expression FOIL method (2x + 3)(x - 4) 2x² - 5x - 12'
            }
        ]
        
        # Calculus Problems
        calculus_problems = [
            {
                'question': 'Find the derivative of f(x) = x³ + 2x² - 5x + 3',
                'solution': 'The derivative is f\'(x) = 3x² + 4x - 5. We apply the power rule to each term.',
                'steps': [
                    'Apply power rule: d/dx[x^n] = nx^(n-1)',
                    'd/dx[x³] = 3x²',
                    'd/dx[2x²] = 4x',
                    'd/dx[-5x] = -5',
                    'd/dx[3] = 0',
                    'Combine: f\'(x) = 3x² + 4x - 5'
                ],
                'method': 'Power Rule',
                'topic': 'Calculus',
                'difficulty': 'Intermediate',
                'content': 'derivative power rule f(x) = x³ + 2x² - 5x + 3 f\'(x) = 3x² + 4x - 5'
            },
            {
                'question': 'Evaluate the integral: ∫(2x + 1)dx',
                'solution': 'The integral is x² + x + C, where C is the constant of integration.',
                'steps': [
                    'Apply power rule for integration: ∫x^n dx = x^(n+1)/(n+1) + C',
                    '∫2x dx = 2(x²/2) = x²',
                    '∫1 dx = x',
                    'Combine: ∫(2x + 1)dx = x² + x + C'
                ],
                'method': 'Power Rule for Integration',
                'topic': 'Calculus',
                'difficulty': 'Beginner',
                'content': 'integral power rule ∫(2x + 1)dx x² + x + C constant integration'
            }
        ]
        
        # Geometry Problems
        geometry_problems = [
            {
                'question': 'Find the area of a circle with radius 5 cm',
                'solution': 'The area is 25π cm² or approximately 78.54 cm². We use the formula A = πr².',
                'steps': [
                    'Use the formula: A = πr²',
                    'Substitute r = 5: A = π(5)²',
                    'Calculate: A = π(25) = 25π',
                    'Approximate: A ≈ 78.54 cm²'
                ],
                'method': 'Circle Area Formula',
                'topic': 'Geometry',
                'difficulty': 'Beginner',
                'content': 'circle area radius 5 cm A = πr² 25π cm² 78.54 cm²'
            },
            {
                'question': 'Find the volume of a cylinder with radius 3 cm and height 8 cm',
                'solution': 'The volume is 72π cm³ or approximately 226.19 cm³. We use the formula V = πr²h.',
                'steps': [
                    'Use the formula: V = πr²h',
                    'Substitute r = 3, h = 8: V = π(3)²(8)',
                    'Calculate: V = π(9)(8) = 72π',
                    'Approximate: V ≈ 226.19 cm³'
                ],
                'method': 'Cylinder Volume Formula',
                'topic': 'Geometry',
                'difficulty': 'Intermediate',
                'content': 'cylinder volume radius 3 cm height 8 cm V = πr²h 72π cm³ 226.19 cm³'
            }
        ]
        
        # Statistics Problems
        statistics_problems = [
            {
                'question': 'Find the mean of the dataset: [2, 4, 6, 8, 10]',
                'solution': 'The mean is 6. We calculate the sum of all values divided by the number of values.',
                'steps': [
                    'Add all values: 2 + 4 + 6 + 8 + 10 = 30',
                    'Count the number of values: 5',
                    'Calculate mean: 30 ÷ 5 = 6'
                ],
                'method': 'Mean Formula',
                'topic': 'Statistics',
                'difficulty': 'Beginner',
                'content': 'mean average dataset [2, 4, 6, 8, 10] sum divided by count 6'
            },
            {
                'question': 'Find the standard deviation of [1, 2, 3, 4, 5]',
                'solution': 'The standard deviation is approximately 1.58. We use the formula for sample standard deviation.',
                'steps': [
                    'Find the mean: (1+2+3+4+5)/5 = 3',
                    'Calculate squared differences: (1-3)², (2-3)², (3-3)², (4-3)², (5-3)²',
                    'Sum squared differences: 4+1+0+1+4 = 10',
                    'Divide by n-1: 10/4 = 2.5',
                    'Take square root: √2.5 ≈ 1.58'
                ],
                'method': 'Standard Deviation Formula',
                'topic': 'Statistics',
                'difficulty': 'Intermediate',
                'content': 'standard deviation sample [1, 2, 3, 4, 5] mean 3 variance 2.5 √2.5 ≈ 1.58'
            }
        ]
        
        # Trigonometry Problems
        trigonometry_problems = [
            {
                'question': 'Find sin(30°)',
                'solution': 'sin(30°) = 1/2 = 0.5. This is a standard trigonometric value.',
                'steps': [
                    'Recall the unit circle or special triangles',
                    'For 30° angle in a 30-60-90 triangle',
                    'sin(30°) = opposite/hypotenuse = 1/2',
                    'Therefore, sin(30°) = 0.5'
                ],
                'method': 'Unit Circle/Special Triangles',
                'topic': 'Trigonometry',
                'difficulty': 'Beginner',
                'content': 'sine 30 degrees sin(30°) 1/2 0.5 unit circle special triangles'
            },
            {
                'question': 'Solve for x: cos(x) = √3/2',
                'solution': 'x = 30° + 360°n or x = 330° + 360°n, where n is any integer.',
                'steps': [
                    'Identify that cos(30°) = √3/2',
                    'Since cosine is positive in QI and QIV',
                    'x = 30° (QI) or x = 360° - 30° = 330° (QIV)',
                    'Add periodicity: x = 30° + 360°n or x = 330° + 360°n'
                ],
                'method': 'Inverse Cosine',
                'topic': 'Trigonometry',
                'difficulty': 'Intermediate',
                'content': 'cosine inverse cos(x) = √3/2 x = 30° 330° periodicity 360°n'
            }
        ]
        
        # Combine all problems
        all_problems = (
            algebra_problems + 
            calculus_problems + 
            geometry_problems + 
            statistics_problems + 
            trigonometry_problems
        )
        
        return all_problems
    
    async def search(self, query: str, limit: int = 5, threshold: float = 0.7) -> List[Dict]:
        """Search for relevant math problems in the knowledge base."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in vector database
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=threshold
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    'question': result.payload['question'],
                    'solution': result.payload['solution'],
                    'steps': result.payload['steps'],
                    'method': result.payload['method'],
                    'topic': result.payload['topic'],
                    'difficulty': result.payload['difficulty'],
                    'similarity_score': result.score
                })
            
            logger.info(f"Found {len(results)} relevant problems for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    async def get_problem_by_id(self, problem_id: int) -> Optional[Dict]:
        """Get a specific problem by ID."""
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[problem_id]
            )
            
            if result:
                payload = result[0].payload
                return {
                    'question': payload['question'],
                    'solution': payload['solution'],
                    'steps': payload['steps'],
                    'method': payload['method'],
                    'topic': payload['topic'],
                    'difficulty': payload['difficulty']
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get problem {problem_id}: {str(e)}")
            return None
    
    async def add_problem(self, problem_data: Dict) -> bool:
        """Add a new problem to the knowledge base."""
        try:
            # Get current collection size for new ID
            collection_info = self.client.get_collection(self.collection_name)
            new_id = collection_info.points_count
            
            # Generate embedding
            content = problem_data.get('content', 
                f"{problem_data['question']} {problem_data['solution']} {problem_data['method']}")
            embedding = self.embedding_model.encode(content).tolist()
            
            # Create point
            point = PointStruct(
                id=new_id,
                vector=embedding,
                payload=problem_data
            )
            
            # Add to collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Added new problem with ID {new_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add problem: {str(e)}")
            return False
    
    async def get_collection_stats(self) -> Dict:
        """Get statistics about the knowledge base."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                'total_problems': collection_info.points_count,
                'vector_dimension': collection_info.config.params.vectors.size,
                'distance_metric': collection_info.config.params.vectors.distance
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {}


# Global knowledge base instance
knowledge_base = MathKnowledgeBase()
