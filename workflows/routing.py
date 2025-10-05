"""
Routing Workflow Pattern Implementation
Direct content to the right specialist agent based on content type or intelligent analysis.
"""

from typing import Any, Dict, Optional
import re

# Import all available agents
from agents.investment_research_agent import investment_research_agent
from agents.earnings_agent import earnings_agent
from agents.news_agent import news_agent
from agents.memory_agent import memory_agent
from agents.market_data_agent import market_data_agent
from agents.evaluator_agent import evaluator_agent


# Agent registry for easy routing
AGENT_REGISTRY = {
    "investment": investment_research_agent,
    "earnings": earnings_agent,
    "news": news_agent,
    "memory": memory_agent,
    "market": market_data_agent,
    "evaluator": evaluator_agent,
}


def route_content(content_type: str, data: str, **kwargs) -> Dict[str, Any]:
    """
    Implement Routing workflow pattern:
    Direct content to the right specialist (earnings, news, or market analyzers)
    
    Args:
        content_type: Type of content (earnings, news, market, memory, investment, evaluator)
        data: Content data to analyze
        **kwargs: Additional parameters to pass to the agent
        
    Returns:
        Dict containing:
        - agent_name: Name of the agent that processed the request
        - content_type: Type of content routed
        - response: Analysis from the appropriate specialist agent
        - status: Success or error status
        
    Example:
        >>> result = route_content("market", "AAPL")
        >>> print(result["response"])
    """
    # Normalize content type
    content_type_lower = content_type.lower().strip()
    
    # Map content types to agents
    routing_map = {
        "earnings": "earnings",
        "financial": "earnings",
        "filings": "earnings",
        "sec": "earnings",
        "quarterly": "earnings",
        "annual": "earnings",
        
        "news": "news",
        "sentiment": "news",
        "articles": "news",
        "headlines": "news",
        
        "market": "market",
        "price": "market",
        "stock": "market",
        "quote": "market",
        "ohlcv": "market",
        "technical": "market",
        
        "memory": "memory",
        "remember": "memory",
        "recall": "memory",
        "store": "memory",
        
        "investment": "investment",
        "research": "investment",
        "analysis": "investment",
        "recommendation": "investment",
        "general": "investment",
        
        "evaluator": "evaluator",
        "evaluate": "evaluator",
        "quality": "evaluator",
        "assess": "evaluator",
    }
    
    # Find the appropriate agent
    agent_key = routing_map.get(content_type_lower)
    
    if not agent_key:
        return {
            "agent_name": "Unknown",
            "content_type": content_type,
            "response": f"Error: Unknown content type '{content_type}'. "
                       f"Valid types: {', '.join(set(routing_map.values()))}",
            "status": "error"
        }
    
    # Get the agent from registry
    agent = AGENT_REGISTRY.get(agent_key)
    
    if not agent:
        return {
            "agent_name": agent_key,
            "content_type": content_type,
            "response": f"Error: Agent '{agent_key}' not found in registry",
            "status": "error"
        }
    
    try:
        # Route to the appropriate agent
        response = agent.run(data, **kwargs)
        
        # Extract content from response (handle different response formats)
        if hasattr(response, 'content'):
            response_content = response.content
        elif isinstance(response, dict) and 'content' in response:
            response_content = response['content']
        else:
            response_content = str(response)
        
        return {
            "agent_name": agent.name,
            "content_type": content_type,
            "response": response_content,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "agent_name": agent.name if agent else "Unknown",
            "content_type": content_type,
            "response": f"Error during routing: {str(e)}",
            "status": "error"
        }


def intelligent_routing(content: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Intelligently route content based on automatic analysis of content type.
    Uses pattern matching and keyword analysis to determine the best agent.
    
    Args:
        content: Raw content to analyze and route
        context: Optional context to help with routing decision
        
    Returns:
        Dict containing:
        - agent_name: Name of the agent that processed the request
        - detected_type: Automatically detected content type
        - confidence: Confidence score of the routing decision (0.0 to 1.0)
        - response: Analysis from the most appropriate agent
        - status: Success or error status
        
    Example:
        >>> result = intelligent_routing("What is the latest stock price for TSLA?")
        >>> print(f"Routed to: {result['agent_name']}")
        >>> print(result['response'])
    """
    # Keywords for each content type with confidence weights
    content_lower = content.lower()
    context_lower = context.lower() if context else ""
    combined_text = f"{content_lower} {context_lower}"
    
    # Define keyword patterns with weights
    patterns = {
        "market": {
            "keywords": ["price", "stock", "quote", "ohlcv", "market data", "ticker", 
                        "volume", "technical", "chart", "trading"],
            "weight": 0.0
        },
        "earnings": {
            "keywords": ["earnings", "financial", "filings", "sec", "quarterly", 
                        "annual", "revenue", "profit", "balance sheet", "10-k", "10-q"],
            "weight": 0.0
        },
        "news": {
            "keywords": ["news", "article", "headlines", "sentiment", "recent", 
                        "announcement", "press release", "media"],
            "weight": 0.0
        },
        "memory": {
            "keywords": ["remember", "recall", "store", "forget", "save", 
                        "retrieve", "memory", "past"],
            "weight": 0.0
        },
        "evaluator": {
            "keywords": ["evaluate", "assess", "quality", "review", "feedback",
                        "score", "rating", "critique"],
            "weight": 0.0
        },
    }
    
    # Calculate weights based on keyword matches
    for category, data in patterns.items():
        for keyword in data["keywords"]:
            if keyword in combined_text:
                data["weight"] += 1.0
    
    # Regex patterns for specific formats (boost confidence)
    if re.search(r'\b[A-Z]{1,5}\b', content):  # Stock ticker pattern
        patterns["market"]["weight"] += 2.0
    
    if re.search(r'\b(10-[KQ]|8-K|earnings report|quarterly report)\b', content_lower):
        patterns["earnings"]["weight"] += 2.0
    
    # Determine the best match
    detected_type = max(patterns.items(), key=lambda x: x[1]["weight"])
    content_type = detected_type[0]
    confidence_score = detected_type[1]["weight"]
    
    # If no strong match found, default to investment research agent
    if confidence_score == 0.0:
        content_type = "investment"
        confidence_score = 0.5  # Medium confidence for default
    else:
        # Normalize confidence score (cap at 1.0)
        confidence_score = min(confidence_score / 5.0, 1.0)
    
    # Route to the determined agent
    result = route_content(content_type, content)
    
    # Add intelligent routing metadata
    result["detected_type"] = content_type
    result["confidence"] = round(confidence_score, 2)
    result["routing_method"] = "intelligent"
    
    return result


def multi_agent_routing(content: str, agent_types: list) -> Dict[str, Any]:
    """
    Route content to multiple agents and aggregate results.
    Useful for comprehensive analysis requiring multiple perspectives.
    
    Args:
        content: Content to analyze
        agent_types: List of agent types to route to (e.g., ["market", "news", "earnings"])
        
    Returns:
        Dict containing:
        - agents_used: List of agents that processed the request
        - responses: Dict mapping agent names to their responses
        - status: Overall status
        
    Example:
        >>> result = multi_agent_routing("AAPL", ["market", "news"])
        >>> for agent, response in result['responses'].items():
        >>>     print(f"{agent}: {response}")
    """
    results = {
        "agents_used": [],
        "responses": {},
        "status": "success"
    }
    
    for agent_type in agent_types:
        try:
            response = route_content(agent_type, content)
            if response["status"] == "success":
                results["agents_used"].append(response["agent_name"])
                results["responses"][response["agent_name"]] = response["response"]
            else:
                results["responses"][agent_type] = f"Error: {response['response']}"
                results["status"] = "partial_success"
        except Exception as e:
            results["responses"][agent_type] = f"Exception: {str(e)}"
            results["status"] = "partial_success"
    
    return results


# CLI demonstration
if __name__ == "__main__":
    print("=" * 80)
    print("ROUTING WORKFLOW PATTERN DEMONSTRATION")
    print("=" * 80)
    
    # Test cases demonstrating different routing scenarios
    test_cases = [
        {
            "description": "Explicit Market Data Routing",
            "content_type": "market",
            "data": "Get the current stock price for TSLA"
        },
        {
            "description": "Explicit News Routing",
            "content_type": "news",
            "data": "Find recent news articles about Microsoft"
        },
        {
            "description": "Explicit Earnings Routing",
            "content_type": "earnings",
            "data": "Analyze the latest earnings report for Apple Inc."
        },
        {
            "description": "Intelligent Routing - Stock Query",
            "method": "intelligent",
            "data": "What is NVDA trading at right now?"
        },
        {
            "description": "Intelligent Routing - News Query",
            "method": "intelligent",
            "data": "Show me the latest headlines about Tesla"
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"Test Case {i}: {test['description']}")
        print(f"{'=' * 80}")
        
        if test.get("method") == "intelligent":
            result = intelligent_routing(test["data"])
            print(f"Detected Type: {result['detected_type']}")
            print(f"Confidence: {result['confidence']}")
        else:
            result = route_content(test["content_type"], test["data"])
        
        print(f"Agent: {result['agent_name']}")
        print(f"Status: {result['status']}")
        print(f"\nResponse Preview:")
        print("-" * 80)
        # Print first 500 characters of response
        response_preview = result['response'][:500]
        print(response_preview)
        if len(result['response']) > 500:
            print("... (truncated)")
        print()
    
    # Interactive mode
    print(f"\n{'=' * 80}")
    print("INTERACTIVE ROUTING MODE")
    print("=" * 80)
    print("Commands:")
    print("  - Type content and it will be intelligently routed")
    print("  - Prefix with 'route:type' for explicit routing (e.g., 'route:market AAPL')")
    print("  - Type 'exit' or 'quit' to end")
    print("=" * 80)
    
    while True:
        user_input = input("\nYour query: ").strip()
        
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting routing demo. Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Check for explicit routing prefix
        if user_input.startswith("route:"):
            parts = user_input.split(" ", 1)
            if len(parts) == 2:
                route_type = parts[0].replace("route:", "")
                content = parts[1]
                result = route_content(route_type, content)
                print(f"\n[Explicit Routing to {route_type}]")
            else:
                print("Invalid routing format. Use: route:type your content")
                continue
        else:
            # Intelligent routing
            result = intelligent_routing(user_input)
            print(f"\n[Intelligent Routing - Type: {result['detected_type']}, "
                  f"Confidence: {result['confidence']}]")
        
        print(f"Agent: {result['agent_name']}")
        print(f"Status: {result['status']}")
        print(f"\n{'-' * 80}")
        print(result['response'])
        print(f"{'-' * 80}")