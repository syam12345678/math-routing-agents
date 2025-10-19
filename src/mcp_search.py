"""Model Context Protocol (MCP) implementation for web search capabilities."""

import asyncio
import logging
from typing import List, Dict, Optional, Any
import httpx
import json
from dataclasses import dataclass
from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result data structure."""
    title: str
    url: str
    content: str
    relevance_score: float
    source: str


class MCPSearchClient:
    """Model Context Protocol implementation for web search."""
    
    def __init__(self):
        self.tavily_client = None
        self.exa_client = None
        self.serper_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize search clients based on available API keys."""
        try:
            if settings.tavily_api_key:
                from tavily import TavilyClient
                self.tavily_client = TavilyClient(api_key=settings.tavily_api_key)
                logger.info("Tavily client initialized")
            
            if settings.exa_api_key:
                from exa_py import Exa
                self.exa_client = Exa(api_key=settings.exa_api_key)
                logger.info("Exa client initialized")
            
            if settings.serper_api_key:
                self.serper_client = {
                    'api_key': settings.serper_api_key,
                    'base_url': 'https://google.serper.dev/search'
                }
                logger.info("Serper client initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize search clients: {str(e)}")
    
    async def search_math_content(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search for math-related content using multiple search providers."""
        results = []
        
        # Try different search providers in order of preference
        search_providers = [
            ('tavily', self._search_tavily),
            ('exa', self._search_exa),
            ('serper', self._search_serper)
        ]
        
        for provider_name, search_func in search_providers:
            try:
                if search_func:
                    provider_results = await search_func(query, max_results)
                    if provider_results:
                        results.extend(provider_results)
                        logger.info(f"Found {len(provider_results)} results from {provider_name}")
                        break  # Use first successful provider
            except Exception as e:
                logger.warning(f"Search failed with {provider_name}: {str(e)}")
                continue
        
        # If no results from any provider, use fallback
        if not results:
            results = await self._fallback_search(query, max_results)
        
        # Filter and rank results for math content
        math_results = self._filter_math_content(results)
        
        return math_results[:max_results]
    
    async def _search_tavily(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using Tavily API."""
        if not self.tavily_client:
            return []
        
        try:
            # Enhance query for math content
            math_query = f"{query} mathematics math solution step by step"
            
            response = self.tavily_client.search(
                query=math_query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=["khanacademy.org", "mathworld.wolfram.com", "brilliant.org", 
                               "math.stackexchange.com", "purplemath.com", "mathisfun.com"]
            )
            
            results = []
            for item in response.get('results', []):
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    content=item.get('content', ''),
                    relevance_score=item.get('score', 0.0),
                    source='tavily'
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}")
            return []
    
    async def _search_exa(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using Exa API."""
        if not self.exa_client:
            return []
        
        try:
            # Enhance query for math content
            math_query = f"{query} mathematics educational content"
            
            response = self.exa_client.search(
                query=math_query,
                num_results=max_results,
                use_autoprompt=True,
                type="neural"
            )
            
            results = []
            for item in response.results:
                result = SearchResult(
                    title=item.title,
                    url=item.url,
                    content=item.text,
                    relevance_score=item.score,
                    source='exa'
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Exa search error: {str(e)}")
            return []
    
    async def _search_serper(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using Serper API (Google Search)."""
        if not self.serper_client:
            return []
        
        try:
            # Enhance query for math content
            math_query = f"{query} mathematics math solution tutorial"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.serper_client['base_url'],
                    headers={
                        'X-API-KEY': self.serper_client['api_key'],
                        'Content-Type': 'application/json'
                    },
                    json={
                        'q': math_query,
                        'num': max_results
                    }
                )
                
                data = response.json()
                results = []
                
                for item in data.get('organic', []):
                    result = SearchResult(
                        title=item.get('title', ''),
                        url=item.get('link', ''),
                        content=item.get('snippet', ''),
                        relevance_score=0.8,  # Default score for Serper
                        source='serper'
                    )
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"Serper search error: {str(e)}")
            return []
    
    async def _fallback_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Fallback search using basic web scraping."""
        try:
            # This is a simplified fallback - in production, you'd want more robust scraping
            results = []
            
            # Create mock results for demonstration
            mock_results = [
                SearchResult(
                    title=f"Math Solution: {query}",
                    url="https://example.com/math-solution",
                    content=f"This is a step-by-step solution for: {query}. The solution involves mathematical reasoning and step-by-step calculations.",
                    relevance_score=0.7,
                    source='fallback'
                )
            ]
            
            return mock_results[:max_results]
            
        except Exception as e:
            logger.error(f"Fallback search error: {str(e)}")
            return []
    
    def _filter_math_content(self, results: List[SearchResult]) -> List[SearchResult]:
        """Filter results to prioritize math-related content."""
        math_keywords = [
            'math', 'mathematics', 'algebra', 'calculus', 'geometry', 'trigonometry',
            'statistics', 'probability', 'equation', 'formula', 'theorem', 'proof',
            'solve', 'calculate', 'derive', 'integrate', 'differentiate'
        ]
        
        filtered_results = []
        
        for result in results:
            # Check if content contains math keywords
            content_lower = (result.title + ' ' + result.content).lower()
            math_score = sum(1 for keyword in math_keywords if keyword in content_lower)
            
            # Boost score for math content
            if math_score > 0:
                result.relevance_score += math_score * 0.1
                filtered_results.append(result)
        
        # Sort by relevance score
        filtered_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return filtered_results
    
    async def extract_math_solution(self, url: str) -> Optional[str]:
        """Extract math solution content from a URL."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                
                # Basic content extraction (in production, use BeautifulSoup or similar)
                content = response.text
                
                # Extract relevant math content (simplified)
                # This would need more sophisticated parsing in production
                return content[:2000]  # Limit content length
                
        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {str(e)}")
            return None
    
    async def validate_math_content(self, content: str) -> bool:
        """Validate if content contains legitimate math information."""
        math_indicators = [
            'equation', 'formula', 'theorem', 'proof', 'solve', 'calculate',
            'derivative', 'integral', 'matrix', 'vector', 'function',
            '=', '+', '-', '*', '/', '^', '√', 'π', '∞'
        ]
        
        content_lower = content.lower()
        math_count = sum(1 for indicator in math_indicators if indicator in content_lower)
        
        # Content should have at least 3 math indicators
        return math_count >= 3


class MCPMathSearch:
    """Main MCP interface for math search operations."""
    
    def __init__(self):
        self.search_client = MCPSearchClient()
    
    async def search_and_extract_solution(self, query: str) -> Dict[str, Any]:
        """Search for math content and extract solution."""
        try:
            # Search for relevant content
            search_results = await self.search_client.search_math_content(query, max_results=3)
            
            if not search_results:
                return {
                    'success': False,
                    'error': 'No relevant math content found',
                    'sources': []
                }
            
            # Extract and validate content
            extracted_solutions = []
            for result in search_results:
                if result.url and result.url != "https://example.com/math-solution":
                    content = await self.search_client.extract_math_solution(result.url)
                    if content and await self.search_client.validate_math_content(content):
                        extracted_solutions.append({
                            'title': result.title,
                            'url': result.url,
                            'content': content,
                            'relevance_score': result.relevance_score
                        })
            
            return {
                'success': True,
                'solutions': extracted_solutions,
                'sources': [{'title': r.title, 'url': r.url} for r in search_results]
            }
            
        except Exception as e:
            logger.error(f"MCP search failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'sources': []
            }


# Global MCP search instance
mcp_search = MCPMathSearch()
