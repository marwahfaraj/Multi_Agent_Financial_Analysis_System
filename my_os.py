"""
Multi-Agent Financial Analysis System - AgentOS
"""
import os
from agno.agent import Agent
from agno.models.google import Gemini
from agno.os import AgentOS
from dotenv import load_dotenv
from workflows.workflow_implementation import workflow

# Load environment variables
load_dotenv()

# Import all our agents
from agents.earnings_agent import earnings_agent
from agents.evaluator_agent import evaluator_agent
from agents.market_data_agent import market_data_agent
from agents.news_agent import news_agent
from agents.memory_agent import memory_agent
from agents.investment_research_agent import investment_research_agent
from agents.preprocessing_agent import preprocessing_agent

# Create AgentOS instance with all our financial analysis agents
agent_os = AgentOS(
    os_id="financial-analysis-os",
    name="Mulit-Agent Financial system",  # Matching the name you registered
    description="Multi-Agent Financial Analysis System for comprehensive stock and market analysis",
    agents=[
        preprocessing_agent,      # Preprocesses user input to extract ticker and intent
        market_data_agent,        # Fetches market data and stock prices
        news_agent,               # Retrieves and analyzes news articles
        earnings_agent,           # Analyzes earnings reports and financial filings
        memory_agent,             # Stores and retrieves financial information
        investment_research_agent,# Synthesizes comprehensive investment research
        evaluator_agent         # Evaluates and improves analysis quality
    ],
    workflows=[
        workflow
    ]
)

app = agent_os.get_app()

if __name__ == "__main__":
    # Default port is 7777; change with port=...
    agent_os.serve(app="my_os:app", reload=True)

