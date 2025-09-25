# TODO: Atul - News API Tools
# Convert your NewsAPI functions from snippet/apicalls.ipynb into Agno tools
# This will be used by the News Agent

from agno.tools import Tool
import requests
import os
from typing import List, Dict, Any, Optional

class NewsAPITools(Tool):
    """Tools for fetching news data from NewsAPI"""
    
    def fetch_news_articles(self, symbol: str, api_key: Optional[str] = None, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch news articles for a given symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            api_key: NewsAPI key (if not provided, will use environment variable)
            page_size: Number of articles to fetch
            
        Returns:
            List of news articles with metadata
        """
        # TODO: Atul - Implement this using your existing function
        # Convert your fetch_news_newsapi function from apicalls.ipynb
        pass
    
    def fetch_financial_news(self, symbol: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch recent financial news for a given symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            days: Number of days to look back
            
        Returns:
            List of recent financial news articles
        """
        # TODO: Atul - Implement this
        pass
