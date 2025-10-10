"""
Shared configuration for all agents
"""
import os
from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL_ID = "gemini-2.5-flash"
DEFAULT_MODEL = Gemini(id=DEFAULT_MODEL_ID)

DEFAULT_AGENT_KWARGS = {
    "model": DEFAULT_MODEL,
    "exponential_backoff": True,
    "retries": 5,
    "delay_between_retries": 5,  # Initial delay in seconds
}
