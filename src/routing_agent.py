"""Routing Agent using LangGraph for knowledge base vs web search decision."""

import logging
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
from src.config import settings
from src.knowledge_base import knowledge_base
from src.mcp_search import mcp_search
from src.guardrails import guardrails

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """State for the routing agent."""
    query: str
    user_id: Optional[str] = None
    knowledge_base_results: Optional[List[Dict]] = None
    web_search_results: Optional[Dict] = None
    routing_decision: Optional[str] = None
    final_response: Optional[Dict] = None
    confidence_score: float = 0.0
    error_message: Optional[str] = None


class MathRoutingAgent:
    """Main routing agent for math questions."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.temperature,
            api_key=settings.openai_api_key
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("search_knowledge_base", self._search_knowledge_base)
        workflow.add_node("make_routing_decision", self._make_routing_decision)
        workflow.add_node("search_web", self._search_web)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("validate_output", self._validate_output)
        workflow.add_node("handle_error", self._handle_error)
        
        # Add edges
        workflow.add_edge("validate_input", "search_knowledge_base")
        workflow.add_edge("search_knowledge_base", "make_routing_decision")
        workflow.add_conditional_edges(
            "make_routing_decision",
            self._should_search_web,
            {
                "web_search": "search_web",
                "knowledge_base": "generate_response",
                "error": "handle_error"
            }
        )
        workflow.add_edge("search_web", "generate_response")
        workflow.add_edge("generate_response", "validate_output")
        workflow.add_edge("validate_output", END)
        workflow.add_edge("handle_error", END)
        
        # Set entry point
        workflow.set_entry_point("validate_input")
        
        return workflow.compile()
    
    async def _validate_input(self, state: AgentState) -> AgentState:
        """Validate input using guardrails."""
        try:
            validated_query = await guardrails.validate_input(
                state.query, 
                state.user_id
            )
            state.query = validated_query.question
            state.user_id = validated_query.user_id
            logger.info("Input validation successful")
        except Exception as e:
            state.error_message = f"Input validation failed: {str(e)}"
            logger.error(f"Input validation failed: {str(e)}")
        
        return state
    
    async def _search_knowledge_base(self, state: AgentState) -> AgentState:
        """Search the knowledge base for relevant content."""
        try:
            if state.error_message:
                return state
            
            results = await knowledge_base.search(
                query=state.query,
                limit=5,
                threshold=0.7
            )
            
            state.knowledge_base_results = results
            
            if results:
                # Calculate confidence based on similarity scores
                avg_score = sum(r['similarity_score'] for r in results) / len(results)
                state.confidence_score = avg_score
                logger.info(f"Found {len(results)} results in knowledge base with avg score {avg_score:.3f}")
            else:
                logger.info("No relevant results found in knowledge base")
                
        except Exception as e:
            state.error_message = f"Knowledge base search failed: {str(e)}"
            logger.error(f"Knowledge base search failed: {str(e)}")
        
        return state
    
    async def _make_routing_decision(self, state: AgentState) -> AgentState:
        """Make routing decision based on knowledge base results."""
        try:
            if state.error_message:
                state.routing_decision = "error"
                return state
            
            # If no results from knowledge base, route to web search
            if not state.knowledge_base_results:
                state.routing_decision = "web_search"
                logger.info("Routing to web search - no knowledge base results")
                return state
            
            # Use LLM to make intelligent routing decision
            routing_prompt = self._create_routing_prompt(state)
            
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a routing agent for a math tutoring system. Decide whether to use knowledge base results or search the web."),
                HumanMessage(content=routing_prompt)
            ])
            
            decision_text = response.content.lower()
            
            if "web search" in decision_text or "search web" in decision_text:
                state.routing_decision = "web_search"
                logger.info("LLM decided to route to web search")
            elif "knowledge base" in decision_text or "use results" in decision_text:
                state.routing_decision = "knowledge_base"
                logger.info("LLM decided to use knowledge base results")
            else:
                # Default decision based on confidence score
                if state.confidence_score >= 0.8:
                    state.routing_decision = "knowledge_base"
                    logger.info("High confidence - using knowledge base results")
                else:
                    state.routing_decision = "web_search"
                    logger.info("Low confidence - routing to web search")
            
        except Exception as e:
            state.error_message = f"Routing decision failed: {str(e)}"
            state.routing_decision = "error"
            logger.error(f"Routing decision failed: {str(e)}")
        
        return state
    
    def _create_routing_prompt(self, state: AgentState) -> str:
        """Create prompt for routing decision."""
        query = state.query
        results = state.knowledge_base_results
        confidence = state.confidence_score
        
        prompt = f"""
        Math Query: "{query}"
        
        Knowledge Base Results Found: {len(results) if results else 0}
        Average Similarity Score: {confidence:.3f}
        
        Top Knowledge Base Results:
        """
        
        if results:
            for i, result in enumerate(results[:3]):
                prompt += f"\n{i+1}. {result['question']} (Score: {result['similarity_score']:.3f})"
                prompt += f"\n   Solution: {result['solution'][:100]}..."
        else:
            prompt += "\nNo results found in knowledge base."
        
        prompt += f"""
        
        Decision Criteria:
        - If knowledge base has high-quality, relevant results (score > 0.8), use knowledge base
        - If knowledge base results are insufficient or low quality, use web search
        - Consider the completeness and accuracy of available solutions
        
        Respond with either "USE KNOWLEDGE BASE" or "SEARCH WEB" followed by a brief reason.
        """
        
        return prompt
    
    def _should_search_web(self, state: AgentState) -> str:
        """Determine next step based on routing decision."""
        if state.error_message:
            return "error"
        elif state.routing_decision == "web_search":
            return "web_search"
        elif state.routing_decision == "knowledge_base":
            return "knowledge_base"
        else:
            return "error"
    
    async def _search_web(self, state: AgentState) -> AgentState:
        """Search the web using MCP."""
        try:
            if state.error_message:
                return state
            
            search_results = await mcp_search.search_and_extract_solution(state.query)
            state.web_search_results = search_results
            
            if search_results['success']:
                logger.info(f"Web search successful - found {len(search_results['solutions'])} solutions")
            else:
                logger.warning(f"Web search failed: {search_results.get('error', 'Unknown error')}")
                
        except Exception as e:
            state.error_message = f"Web search failed: {str(e)}"
            logger.error(f"Web search failed: {str(e)}")
        
        return state
    
    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate final response based on available data."""
        try:
            if state.error_message:
                return state
            
            response_data = await self._create_response(state)
            state.final_response = response_data
            
            logger.info("Response generated successfully")
            
        except Exception as e:
            state.error_message = f"Response generation failed: {str(e)}"
            logger.error(f"Response generation failed: {str(e)}")
        
        return state
    
    async def _create_response(self, state: AgentState) -> Dict[str, Any]:
        """Create the final response based on available data."""
        query = state.query
        
        if state.routing_decision == "knowledge_base" and state.knowledge_base_results:
            # Use knowledge base results
            best_result = state.knowledge_base_results[0]
            
            response = {
                'solution': best_result['solution'],
                'steps': best_result['steps'],
                'method': best_result['method'],
                'confidence': best_result['similarity_score'],
                'sources': [f"Knowledge Base - {best_result['topic']}"],
                'feedback_requested': True,
                'routing_source': 'knowledge_base'
            }
            
        elif state.routing_decision == "web_search" and state.web_search_results:
            # Use web search results
            if state.web_search_results['success'] and state.web_search_results['solutions']:
                # Generate solution from web content using LLM
                web_solution = await self._generate_solution_from_web_content(
                    query, 
                    state.web_search_results['solutions']
                )
                
                response = {
                    'solution': web_solution['solution'],
                    'steps': web_solution['steps'],
                    'method': web_solution['method'],
                    'confidence': 0.7,  # Default confidence for web results
                    'sources': [source['title'] for source in state.web_search_results['sources']],
                    'feedback_requested': True,
                    'routing_source': 'web_search'
                }
            else:
                # Fallback response
                response = {
                    'solution': f"I apologize, but I couldn't find a complete solution for '{query}' in my knowledge base or through web search. Please try rephrasing your question or providing more specific details.",
                    'steps': ["Unable to provide step-by-step solution"],
                    'method': "Unable to determine",
                    'confidence': 0.0,
                    'sources': [],
                    'feedback_requested': True,
                    'routing_source': 'none'
                }
        else:
            # Error response
            response = {
                'solution': f"I encountered an error while processing your question: '{query}'. Please try again.",
                'steps': ["Error occurred during processing"],
                'method': "Error",
                'confidence': 0.0,
                'sources': [],
                'feedback_requested': True,
                'routing_source': 'error'
            }
        
        return response
    
    async def _generate_solution_from_web_content(self, query: str, web_solutions: List[Dict]) -> Dict[str, Any]:
        """Generate solution from web search content using LLM."""
        try:
            # Prepare context from web solutions
            context = ""
            for i, solution in enumerate(web_solutions[:2]):  # Use top 2 results
                context += f"\nSource {i+1}: {solution['title']}\n"
                context += f"Content: {solution['content'][:500]}...\n"
            
            prompt = f"""
            Based on the following web search results, generate a step-by-step solution for this math question: "{query}"
            
            Web Search Results:
            {context}
            
            Please provide:
            1. A clear, step-by-step solution
            2. The method used
            3. Break down the solution into logical steps
            
            Format your response as JSON:
            {{
                "solution": "Complete solution explanation",
                "steps": ["Step 1", "Step 2", "Step 3"],
                "method": "Method name"
            }}
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a math tutor. Generate clear, step-by-step solutions from web content."),
                HumanMessage(content=prompt)
            ])
            
            # Parse JSON response
            try:
                solution_data = json.loads(response.content)
                return solution_data
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'solution': response.content,
                    'steps': ["Solution generated from web content"],
                    'method': "Web Search Analysis"
                }
                
        except Exception as e:
            logger.error(f"Failed to generate solution from web content: {str(e)}")
            return {
                'solution': f"Based on web search results, here's a solution for: {query}",
                'steps': ["Solution derived from web content"],
                'method': "Web Search"
            }
    
    async def _validate_output(self, state: AgentState) -> AgentState:
        """Validate output using guardrails."""
        try:
            if state.error_message or not state.final_response:
                return state
            
            validated_response = await guardrails.validate_output(state.final_response)
            state.final_response = validated_response.dict()
            logger.info("Output validation successful")
            
        except Exception as e:
            state.error_message = f"Output validation failed: {str(e)}"
            logger.error(f"Output validation failed: {str(e)}")
        
        return state
    
    async def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors gracefully."""
        error_msg = state.error_message or "Unknown error occurred"
        
        state.final_response = {
            'solution': f"I apologize, but I encountered an error: {error_msg}. Please try again with a different question.",
            'steps': ["Error occurred"],
            'method': "Error",
            'confidence': 0.0,
            'sources': [],
            'feedback_requested': True,
            'routing_source': 'error'
        }
        
        logger.error(f"Error handled: {error_msg}")
        return state
    
    async def process_query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a math query through the routing agent."""
        try:
            # Create initial state
            initial_state = AgentState(query=query, user_id=user_id)
            
            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            # Return the final response
            if final_state.final_response:
                return {
                    'success': True,
                    'response': final_state.final_response,
                    'routing_decision': final_state.routing_decision,
                    'confidence': final_state.confidence_score
                }
            else:
                return {
                    'success': False,
                    'error': final_state.error_message or "Unknown error",
                    'response': None
                }
                
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }


# Global routing agent instance
routing_agent = MathRoutingAgent()
