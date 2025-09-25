# TODO: Atul - Market Data Agent
# This agent will be responsible for fetching market data using APIs
# Should integrate with tools/yahoo_finance_tools.py and other data sources

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()

