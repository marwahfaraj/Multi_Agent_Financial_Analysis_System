# TODO: Atul - Market Data Agent
# This agent will be responsible for fetching market data using APIs
# Should integrate with tools/yahoo_finance_tools.py and other data sources

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv

# -----------------------------
# Enable postponed evaluation of annotations (helps with forward references and typing in older Python versions).
# -----------------------------
from __future__ import annotations

# -----------------------------
# Import the standard library 'os' module for file paths and environment variables.
# -----------------------------
import os

# -----------------------------
# Import 'yaml' to read configuration from a YAML file (params.yaml).
# -----------------------------
import yaml

# -----------------------------
# Import 'argparse' to parse command-line arguments for the CLI entrypoint.
# -----------------------------
import argparse

# -----------------------------
# Import 'json' to serialize tool outputs to JSON strings for LLM-friendly responses.
# -----------------------------
import json

# -----------------------------
# Import dataclass utilities for simple configuration containers.
# -----------------------------
from dataclasses import dataclass

# -----------------------------
# Import typing helpers for type hints (readability and editor support).
# -----------------------------
from typing import Any, Dict, List

# -----------------------------
# Import 'load_dotenv' to load secrets and settings from a .env file into environment variables.
# -----------------------------
from dotenv import load_dotenv

# -----------------------------
# Import Agno's Agent (agent runtime), Gemini model adapter, and tool decorator for tool-calling.
# -----------------------------
from agno.agent import Agent

# -----------------------------
# Import the Gemini (Google) model connector used by Agno.
# -----------------------------
from agno.models.google import Gemini

# -----------------------------
# Import the tool decorator to expose Python functions as callable tools to the agent.
# -----------------------------
from agno.tools import tool

# -----------------------------
# Import pandas for data handling (time series, DataFrames).
# -----------------------------
import pandas as pd

# -----------------------------
# Import numpy for numeric conversions and safe JSON serialization.
# -----------------------------
import numpy as np

# -----------------------------
# Try to import yfinance for market data; if not available, set yf=None so tools can error gracefully.
# -----------------------------
try:
    import yfinance as yf
# -----------------------------
# If yfinance import fails (not installed or blocked), set yf to None so tools can handle it.
# -----------------------------
except Exception:
    yf = None


load_dotenv(".env")

# ==============================
# Constants / String Registry
# ==============================
# -----------------------------
# Define a central registry of constants so strings/keys/defaults live in one place for easy maintenance.
# -----------------------------
class FIN_ANALYST_CONST:
    # ---- Files / Encoding ----
    # -----------------------------
    # The filename for dotenv; used by load_dotenv to bring env vars into the process.
    # -----------------------------
    DOTENV_FILE = ".env"
    # -----------------------------
    # Default path to the YAML params file (in the project root).
    # -----------------------------
    YAML_DEFAULT_PATH = os.path.join(os.getcwd(), "params.yaml")
    # -----------------------------
    # Default file encoding when reading text files.
    # -----------------------------
    FILE_ENCODING = "utf-8"

    # ---- Env vars ----
    # -----------------------------
    # Environment variable name for selecting the Gemini model id.
    # -----------------------------
    ENV_GEMINI_MODEL = "GEMINI_MODEL"
    # -----------------------------
    # Environment variable name for the Gemini API key.
    # -----------------------------
    ENV_GEMINI_API_KEY = "GEMINI_API_KEY"
    # -----------------------------
    # Alternative environment variable name (Google API key) that also works with Gemini.
    # -----------------------------
    ENV_GOOGLE_API_KEY = "GOOGLE_API_KEY"

    # ---- Defaults ----
    # -----------------------------
    # Fallback model id to use if ENV_GEMINI_MODEL is not set.
    # -----------------------------
    DEFAULT_MODEL_ID = "gemini-2.5-flash"
    # -----------------------------
    # Default agent key to look up inside params.yaml.
    # -----------------------------
    DEFAULT_AGENT_KEY = "market_data_analyst"

    # ---- YAML keys ----
    # -----------------------------
    # Top-level key holding all agents in params.yaml.
    # -----------------------------
    YAML_AGENTS = "agents"
    # -----------------------------
    # Top-level key holding default settings in params.yaml.
    # -----------------------------
    YAML_DEFAULTS = "defaults"
    # -----------------------------
    # Key inside defaults for shared instructions applied to all agents.
    # -----------------------------
    YAML_GLOBAL_INSTR = "global_instructions"
    # -----------------------------
    # Key inside an agent for its specific instructions.
    # -----------------------------
    YAML_INSTRUCTIONS = "instructions"
    # -----------------------------
    # Key for an agent’s description text.
    # -----------------------------
    YAML_DESCRIPTION = "description"
    # -----------------------------
    # Key for an agent’s display name.
    # -----------------------------
    YAML_NAME = "name"

    # ---- Tool names & descriptions ----
    # -----------------------------
    # Public tool name for fetching a quote (used by LLM to call the tool).
    # -----------------------------
    TOOL_FETCH_QUOTE = "fetch_quote"
    # -----------------------------
    # Human-readable description shown to the LLM describing what the quote tool does.
    # -----------------------------
    TOOL_FETCH_QUOTE_DESC = (
        "Get latest price and basic metrics for a stock symbol using yfinance."
    )

    # -----------------------------
    # Public tool name for fetching OHLCV history (used by LLM to call the tool).
    # -----------------------------
    TOOL_FETCH_OHLCV = "fetch_ohlcv"
    # -----------------------------
    # Human-readable description for the OHLCV tool.
    # -----------------------------
    TOOL_FETCH_OHLCV_DESC = "Download OHLCV price history for a symbol via yfinance."

    # ---- yfinance parameters ----
    # -----------------------------
    # yfinance download() param: group columns by "column" (helps avoid nested MultiIndex surprises).
    # -----------------------------
    YF_GROUP_BY = "column"
    # -----------------------------
    # yfinance download() param: do not use multi-threaded downloads (stability).
    # -----------------------------
    YF_THREADS = False
    # -----------------------------
    # yfinance download() param: do not show progress bars (cleaner logs).
    # -----------------------------
    YF_PROGRESS = False
    # -----------------------------
    # yfinance download()/history() param: auto-adjust for splits/dividends.
    # -----------------------------
    YF_AUTO_ADJUST = True
    # -----------------------------
    # Default lookback period for OHLCV history.
    # -----------------------------
    YF_DEF_PERIOD = "1y"
    # -----------------------------
    # Default bar interval for OHLCV history.
    # -----------------------------
    YF_DEF_INTERVAL = "1d"
    # -----------------------------
    # Short recent period used when we only need a last close (fallback in fetch_quote).
    # -----------------------------
    YF_RECENT_PERIOD = "5d"
    # -----------------------------
    # Daily bar interval (paired with recent period) for last close fallback.
    # -----------------------------
    YF_DAILY_INTERVAL = "1d"

    # ---- Data / Columns / Keys ----
    # -----------------------------
    # The columns we care about for OHLCV data.
    # -----------------------------
    OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")
    # -----------------------------
    # Name of the date column when we convert index to a column.
    # -----------------------------
    COL_DATE = "Date"

    # -----------------------------
    # Common JSON keys used in tool outputs.
    # -----------------------------
    KEY_SYMBOL = "symbol"
    KEY_ROWS = "rows"
    KEY_PERIOD = "period"
    KEY_INTERVAL = "interval"
    KEY_TAIL5 = "tail5"
    KEY_LAST_PRICE = "last_price"
    KEY_CURRENCY = "currency"
    KEY_EXCHANGE = "exchange"
    KEY_SHORT_NAME = "shortName"
    KEY_ERROR = "error"
    KEY_OHLCV = "ohlcv"

    # ---- Errors / Messages ----
    # -----------------------------
    # Error message when yfinance is unavailable.
    # -----------------------------
    ERR_YF_NOT_INSTALLED = "yfinance not installed"
    # -----------------------------
    # Error message when Gemini credentials are missing.
    # -----------------------------
    ERR_MISSING_GEMINI_KEY = (
        "Missing Gemini API key. Set GEMINI_API_KEY or GOOGLE_API_KEY."
    )
    # -----------------------------
    # Error template when the requested agent key is not defined in params.yaml.
    # -----------------------------
    ERR_AGENT_NOT_FOUND = (
        "Agent key '{key}' not found in params.yaml. Available: {available}"
    )
    # -----------------------------
    # Prefix used when returning error strings from the chatbot method.
    # -----------------------------
    ERR_PREFIX = "**ERROR:** "

    # ---- Agent metadata ----
    # -----------------------------
    # Default name for the agent when YAML doesn't provide one.
    # -----------------------------
    DEFAULT_AGENT_NAME = "Finance Agent"
    # -----------------------------
    # Default description for the agent when YAML doesn't provide one.
    # -----------------------------
    DEFAULT_AGENT_DESC = "Financial analyst agent."
    # -----------------------------
    # Default single-line instruction when no instructions are provided.
    # -----------------------------
    DEFAULT_FALLBACK_INSTR = (
        "Be concise and factual. Use the provided tools when helpful."
    )

    # ---- CLI ----
    # -----------------------------
    # CLI description shown in --help for the script.
    # -----------------------------
    ARGPARSE_DESC = "Financial Analyst Agent."
    # -----------------------------
    # CLI help text for the positional 'query' argument.
    # -----------------------------
    ARGPARSE_QUERY_HELP = "Your question"

    # ---- Misc ----
    # -----------------------------
    # Placeholder string used when no agents are available in YAML.
    # -----------------------------
    AVAILABLE_NONE = "<none>"


# -----------------------------
# Load environment variables from the .env file specified in constants.
# -----------------------------
load_dotenv(FIN_ANALYST_CONST.DOTENV_FILE)


# -----------------------------
# Helper: convert numpy/pandas types to JSON-safe types (so json.dumps won't fail).
# -----------------------------
def _json_safe(o):
    """Make numpy/pandas types JSON-serializable."""
    # -----------------------------
    # If it's a NumPy number, convert to native Python int/float.
    # -----------------------------
    if isinstance(o, (np.integer, np.floating)):
        return o.item()
    # -----------------------------
    # If it's a NumPy array, convert to a Python list.
    # -----------------------------
    if isinstance(o, (np.ndarray,)):
        return o.tolist()
    # -----------------------------
    # Fallback: string representation for anything else (e.g., Timestamp).
    # -----------------------------
    return str(o)


# -----------------------------
# Helper: normalize a YAML value (string or list of strings) into a clean list of strings.
# -----------------------------
def _to_list(x) -> List[str]:
    """Normalize YAML value to a list of strings."""
    # -----------------------------
    # If already a list, coerce each element to string.
    # -----------------------------
    if isinstance(x, list):
        return [str(i) for i in x]
    # -----------------------------
    # If a non-empty string, wrap it in a list.
    # -----------------------------
    if isinstance(x, str) and x.strip():
        return [x.strip()]
    # -----------------------------
    # Otherwise, return an empty list.
    # -----------------------------
    return []


# -----------------------------
# Tool: fetch_quote
# Exposes a function the agent can call to get latest price info for a symbol.
# Returns a JSON string so the LLM sees a deterministic, structured payload.
# -----------------------------
@tool(
    name=FIN_ANALYST_CONST.TOOL_FETCH_QUOTE,
    description=FIN_ANALYST_CONST.TOOL_FETCH_QUOTE_DESC,
)
def fetch_quote(symbol: str) -> str:
    """Return latest quote details as a JSON string."""
    # -----------------------------
    # If yfinance is missing, return a clear error JSON.
    # -----------------------------
    if yf is None:
        return json.dumps(
            {FIN_ANALYST_CONST.KEY_ERROR: FIN_ANALYST_CONST.ERR_YF_NOT_INSTALLED}
        )
    try:
        # -----------------------------
        # Create a yfinance Ticker object for the provided symbol.
        # -----------------------------
        t = yf.Ticker(symbol)

        # -----------------------------
        # Attempt to use fast_info (faster, lighter) if available.
        # -----------------------------
        fi = getattr(t, "fast_info", None)
        # -----------------------------
        # Initialize price as None; we'll fill it from fast_info or history.
        # -----------------------------
        price = None
        # -----------------------------
        # If fast_info exists, read last price or last close.
        # -----------------------------
        if fi:
            price = getattr(fi, "last_price", None) or getattr(fi, "last_close", None)

        # -----------------------------
        # If fast_info didn't yield a price, pull a short history and take the last close.
        # -----------------------------
        if price is None:
            hist = t.history(
                period=FIN_ANALYST_CONST.YF_RECENT_PERIOD,
                interval=FIN_ANALYST_CONST.YF_DAILY_INTERVAL,
                auto_adjust=FIN_ANALYST_CONST.YF_AUTO_ADJUST,
            )
            # -----------------------------
            # Ensure history exists and has rows before reading the last close.
            # -----------------------------
            if hasattr(hist, "empty") and not hist.empty:
                price = float(hist["Close"].iloc[-1])

        # -----------------------------
        # Prepare a dict for additional metadata (currency, exchange, names).
        # Some yfinance builds throttle .info; we catch/ignore errors gracefully.
        # -----------------------------
        info = {}
        try:
            info = t.info or {}
        except Exception:
            info = {}

        # -----------------------------
        # Build the JSON-serializable payload with price and metadata fields.
        # -----------------------------
        out = {
            FIN_ANALYST_CONST.KEY_SYMBOL: symbol,
            FIN_ANALYST_CONST.KEY_LAST_PRICE: price,
            FIN_ANALYST_CONST.KEY_CURRENCY: (
                getattr(fi, "currency", None) if fi else info.get("currency")
            ),
            FIN_ANALYST_CONST.KEY_EXCHANGE: info.get("exchange")
            or info.get("fullExchangeName"),
            FIN_ANALYST_CONST.KEY_SHORT_NAME: info.get("shortName")
            or info.get("longName"),
        }
        # -----------------------------
        # Serialize the dict to a JSON string (default=_json_safe covers NumPy types).
        # -----------------------------
        return json.dumps(out, default=_json_safe)
    # -----------------------------
    # On any exception (network, symbol not found, etc.), return a structured error JSON.
    # -----------------------------
    except Exception as e:
        return json.dumps(
            {FIN_ANALYST_CONST.KEY_SYMBOL: symbol, FIN_ANALYST_CONST.KEY_ERROR: f"{e}"}
        )


# -----------------------------
# Tool: fetch_ohlcv
# Exposes a function the agent can call to get time-series bars and a 5-row preview.
# Returns a JSON string to keep outputs deterministic for the LLM.
# -----------------------------
@tool(
    name=FIN_ANALYST_CONST.TOOL_FETCH_OHLCV,
    description=FIN_ANALYST_CONST.TOOL_FETCH_OHLCV_DESC,
)
def fetch_ohlcv(
    symbol: str,
    period: str = FIN_ANALYST_CONST.YF_DEF_PERIOD,
    interval: str = FIN_ANALYST_CONST.YF_DEF_INTERVAL,
) -> str:
    """
    Return last 5 rows of OHLCV (as JSON string) for symbol/period/interval using yfinance.
    Handles MultiIndex columns and numpy types.
    """
    # -----------------------------
    # If yfinance isn't installed, return a structured error JSON.
    # -----------------------------
    if yf is None:
        return json.dumps(
            {FIN_ANALYST_CONST.KEY_ERROR: FIN_ANALYST_CONST.ERR_YF_NOT_INSTALLED}
        )
    try:
        # -----------------------------
        # Download price history from Yahoo via yfinance for the given period/interval.
        # -----------------------------
        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=FIN_ANALYST_CONST.YF_PROGRESS,
            auto_adjust=FIN_ANALYST_CONST.YF_AUTO_ADJUST,
            group_by=FIN_ANALYST_CONST.YF_GROUP_BY,
            threads=FIN_ANALYST_CONST.YF_THREADS,
        )

        # -----------------------------
        # If we got nothing back, return an empty payload with rows=0.
        # -----------------------------
        if df is None or df.empty:
            return json.dumps(
                {
                    FIN_ANALYST_CONST.KEY_SYMBOL: symbol,
                    FIN_ANALYST_CONST.KEY_ROWS: 0,
                    FIN_ANALYST_CONST.KEY_OHLCV: [],
                }
            )

        # -----------------------------
        # yfinance can return MultiIndex columns (e.g., ('Close','AAPL')); flatten to single-level.
        # -----------------------------
        if isinstance(df.columns, pd.MultiIndex):
            try:
                # -----------------------------
                # If the symbol appears in the deepest level, slice that level out first.
                # -----------------------------
                if symbol in df.columns.get_level_values(-1):
                    df = df.xs(symbol, axis=1, level=-1)
                # -----------------------------
                # Otherwise try slicing the first level.
                # -----------------------------
                elif symbol in df.columns.get_level_values(0):
                    df = df.xs(symbol, axis=1, level=0)
            # -----------------------------
            # If slicing fails for any reason, ignore and continue to flatten generically.
            # -----------------------------
            except Exception:
                pass
            # -----------------------------
            # If it's still MultiIndex after slicing, collapse tuples -> string using the 1st element.
            # -----------------------------
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [
                    str(col[0]) if isinstance(col, tuple) and len(col) > 0 else str(col)
                    for col in df.columns
                ]
        # -----------------------------
        # If columns were already flat, ensure all names are strings.
        # -----------------------------
        else:
            df.columns = [str(c) for c in df.columns]

        # -----------------------------
        # Keep only the standard OHLCV columns that are present.
        # -----------------------------
        keep = [c for c in FIN_ANALYST_CONST.OHLCV_COLUMNS if c in df.columns]
        # -----------------------------
        # If none of the expected columns are present, return an empty payload.
        # -----------------------------
        if not keep:
            return json.dumps(
                {
                    FIN_ANALYST_CONST.KEY_SYMBOL: symbol,
                    FIN_ANALYST_CONST.KEY_ROWS: 0,
                    FIN_ANALYST_CONST.KEY_OHLCV: [],
                }
            )

        # -----------------------------
        # Subset to columns of interest and normalize the index as a datetime index.
        # -----------------------------
        df = df[keep].copy()
        # -----------------------------
        # Convert the DataFrame index to pandas datetime for proper time ordering.
        # -----------------------------
        df.index = pd.to_datetime(df.index)
        # -----------------------------
        # Ensure rows are sorted ascending by time.
        # -----------------------------
        df.sort_index(inplace=True)

        # -----------------------------
        # Take the last 5 rows and reset the index into a column.
        # -----------------------------
        tail = df.tail(5).reset_index()
        # -----------------------------
        # Make sure the first column is named 'Date' for consistent JSON output shape.
        # -----------------------------
        if tail.columns[0] != FIN_ANALYST_CONST.COL_DATE:
            tail.rename(
                columns={tail.columns[0]: FIN_ANALYST_CONST.COL_DATE}, inplace=True
            )
        # -----------------------------
        # Convert date column to strings so json.dumps can serialize it.
        # -----------------------------
        tail[FIN_ANALYST_CONST.COL_DATE] = tail[FIN_ANALYST_CONST.COL_DATE].astype(str)

        # -----------------------------
        # Build the final payload including meta info and the 5-row preview.
        # -----------------------------
        payload = {
            FIN_ANALYST_CONST.KEY_SYMBOL: symbol,
            FIN_ANALYST_CONST.KEY_ROWS: int(len(df)),
            FIN_ANALYST_CONST.KEY_PERIOD: period,
            FIN_ANALYST_CONST.KEY_INTERVAL: interval,
            FIN_ANALYST_CONST.KEY_TAIL5: tail.to_dict(orient="records"),
        }
        # -----------------------------
        # Serialize payload to JSON; _json_safe makes NumPy types safe.
        # -----------------------------
        return json.dumps(payload, default=_json_safe)
    # -----------------------------
    # Catch-all: return a structured error JSON with the exception message.
    # -----------------------------
    except Exception as e:
        return json.dumps(
            {FIN_ANALYST_CONST.KEY_SYMBOL: symbol, FIN_ANALYST_CONST.KEY_ERROR: f"{e}"}
        )


# -----------------------------
# Dataclass: tiny container for CLI/runtime config (params path + agent key).
# -----------------------------
@dataclass
class FinancialAnalystAgentConfig:
    # -----------------------------
    # Path to the YAML configuration file.
    # -----------------------------
    paramsPath: str = FIN_ANALYST_CONST.YAML_DEFAULT_PATH
    # -----------------------------
    # Which agent block to use from params.yaml (agents.<agent_key>).
    # -----------------------------
    agent_key: str = FIN_ANALYST_CONST.DEFAULT_AGENT_KEY


# -----------------------------
# The main agent wrapper that loads YAML, builds the Agno Agent, and routes calls.
# -----------------------------
class FinancialAnalystAgent:
    # -----------------------------
    # Constructor: optionally accept a specific agent_key to pick a different agent block.
    # -----------------------------
    def __init__(self, agent_key: str | None = None):
        # -----------------------------
        # Initialize dataclass config with defaults.
        # -----------------------------
        self.cfg = FinancialAnalystAgentConfig()
        # -----------------------------
        # If caller provided an override for agent key, use it.
        # -----------------------------
        if agent_key:
            self.cfg.agent_key = agent_key

        # -----------------------------
        # Open and read the YAML params file into a dict (or {} if empty).
        # -----------------------------
        with open(
            self.cfg.paramsPath, "r", encoding=FIN_ANALYST_CONST.FILE_ENCODING
        ) as f:
            self.params: Dict[str, Any] = yaml.safe_load(f) or {}

        # -----------------------------
        # Extract the agents mapping from YAML (may be empty dict).
        # -----------------------------
        agents = self.params.get(FIN_ANALYST_CONST.YAML_AGENTS) or {}
        # -----------------------------
        # Validate that the chosen agent key exists; if not, raise a helpful error.
        # -----------------------------
        if self.cfg.agent_key not in agents:
            available = ", ".join(agents.keys()) or FIN_ANALYST_CONST.AVAILABLE_NONE
            raise RuntimeError(
                FIN_ANALYST_CONST.ERR_AGENT_NOT_FOUND.format(
                    key=self.cfg.agent_key, available=available
                )
            )

        # -----------------------------
        # Load global defaults and the specific agent’s configuration block.
        # -----------------------------
        self.defaults: Dict[str, Any] = (
            self.params.get(FIN_ANALYST_CONST.YAML_DEFAULTS) or {}
        )
        # -----------------------------
        # Shortcut to the active agent’s config dictionary.
        # -----------------------------
        self.agent_cfg: Dict[str, Any] = agents[self.cfg.agent_key] or {}

        # -----------------------------
        # Resolve model id from env (fallback to constant), and pick the API key from GEMINI/GOOGLE envs.
        # -----------------------------
        self.gemini_model_id = os.getenv(
            FIN_ANALYST_CONST.ENV_GEMINI_MODEL, FIN_ANALYST_CONST.DEFAULT_MODEL_ID
        )
        # -----------------------------
        # Prefer GEMINI_API_KEY; if absent, try GOOGLE_API_KEY.
        # -----------------------------
        self.gemini_api_key = os.getenv(
            FIN_ANALYST_CONST.ENV_GEMINI_API_KEY
        ) or os.getenv(FIN_ANALYST_CONST.ENV_GOOGLE_API_KEY)
        # -----------------------------
        # If neither key is present, fail fast with a clear error message.
        # -----------------------------
        if not self.gemini_api_key:
            raise RuntimeError(FIN_ANALYST_CONST.ERR_MISSING_GEMINI_KEY)

        # -----------------------------
        # Build the description string (YAML override or default).
        # -----------------------------
        self.description: str = self.agent_cfg.get(
            FIN_ANALYST_CONST.YAML_DESCRIPTION, FIN_ANALYST_CONST.DEFAULT_AGENT_DESC
        )
        # -----------------------------
        # Read in shared/global instructions from YAML defaults and normalize to list.
        # -----------------------------
        global_instr = _to_list(
            self.defaults.get(FIN_ANALYST_CONST.YAML_GLOBAL_INSTR) or []
        )
        # -----------------------------
        # Read in agent-specific instructions from YAML and normalize to list.
        # -----------------------------
        agent_instr = _to_list(
            self.agent_cfg.get(FIN_ANALYST_CONST.YAML_INSTRUCTIONS) or []
        )
        # -----------------------------
        # Final instruction list is the concatenation of global + agent-specific,
        # or a single fallback instruction if both are empty.
        # -----------------------------
        self.instructions: List[str] = global_instr + agent_instr or [
            FIN_ANALYST_CONST.DEFAULT_FALLBACK_INSTR
        ]

    # -----------------------------
    # Public method: runs the Agno agent with the provided user query and returns text.
    # -----------------------------
    def chatbot(self, userQuery: str) -> str:
        # -----------------------------
        # Construct the Agno Agent with Gemini model and our two tools.
        # -----------------------------
        agno_agent = Agent(
            name=self.agent_cfg.get(
                FIN_ANALYST_CONST.YAML_NAME, FIN_ANALYST_CONST.DEFAULT_AGENT_NAME
            ),
            description=self.description,
            model=Gemini(id=self.gemini_model_id, api_key=self.gemini_api_key),
            tools=[fetch_quote, fetch_ohlcv],
            instructions=self.instructions,
            add_datetime_to_context=True,
            markdown=True,
        )
        try:
            # -----------------------------
            # Execute the agent with the user's query; Agno returns an object with .content in new versions.
            # -----------------------------
            resp = agno_agent.run(userQuery)
            # -----------------------------
            # Prefer .content if present (clean, final text).
            # -----------------------------
            content = getattr(resp, "content", None)
            # -----------------------------
            # If .content exists, return it now.
            # -----------------------------
            if content:
                return content
            # -----------------------------
            # For older Agno versions, convert response to dict and read last message.
            # -----------------------------
            if hasattr(resp, "to_dict"):
                d = resp.to_dict()
                try:
                    return d["messages"][-1]["content"]
                except Exception:
                    pass
            # -----------------------------
            # As a final fallback, coerce the whole response to string.
            # -----------------------------
            return str(resp)
        # -----------------------------
        # Catch any runtime exception and return it as a prefixed error string (does not crash the process).
        # -----------------------------
        except Exception as e:
            return f"{FIN_ANALYST_CONST.ERR_PREFIX}{e}"


# -----------------------------
# CLI entrypoint: run the agent from the command line.
# -----------------------------
if __name__ == "__main__":
    # -----------------------------
    # Create an argparse parser with a helpful description.
    # -----------------------------
    parser = argparse.ArgumentParser(description=FIN_ANALYST_CONST.ARGPARSE_DESC)
    # -----------------------------
    # Define a single positional argument 'query' for the user's question.
    # -----------------------------
    parser.add_argument("query", type=str, help=FIN_ANALYST_CONST.ARGPARSE_QUERY_HELP)
    # -----------------------------
    # Parse CLI args from sys.argv.
    # -----------------------------
    args = parser.parse_args()

    # -----------------------------
    # Instantiate the agent wrapper with the default agent key (can be changed in code or via a different script).
    # -----------------------------
    agent = FinancialAnalystAgent(agent_key=FIN_ANALYST_CONST.DEFAULT_AGENT_KEY)
    # -----------------------------
    # Run the chatbot with the provided query and print the result to stdout.
    # -----------------------------
    print(agent.chatbot(args.query))



"""
EXAMPLE Using CLI:: 

Command to use: python market_data_agent.py "Compare AAPL vs MSFT 6 month  performance,  vol and average moving value."

Here's a comparison of Apple (AAPL) and Microsoft (MSFT) over the past 6 months (approximately 127 trading days), as of September 24, 2025:

### Key Metrics Snapshot (6-Month Performance)

**Apple (AAPL)**

*   **Latest Close (2025-09-24):** $252.31
*   **6-Month Performance (Approximate):**
    *   **Start of Period (2025-03-25):** $170.85 (estimated from first available data point)
    *   **Percentage Change:** ~ +47.68%
*   **Average Daily Volume (Last 5 days):** ~ 83.6 million shares/day
*   **Average Moving Value (Last 5 days):** ~$250.75

**Microsoft (MSFT)**

*   **Latest Close (2025-09-24):** $510.15
*   **6-Month Performance (Approximate):**
    *   **Start of Period (2025-03-25):** $424.32 (estimated from first available data point)
    *   **Percentage Change:** ~ +20.23%
*   **Average Daily Volume (Last 5 days):** ~ 24.9 million shares/day
*   **Average Moving Value (Last 5 days):** ~$510.08

###  News Insights and Likely Impact

(No specific news was provided in the query, so this section will focus on general market observations based on the data.)

Apple has shown significantly stronger performance over the last six months, with a nearly 48% increase in its stock price, compared to Microsoft's roughly 20% gain. This could suggest positive sentiment around Apple's recent product cycles, services growth, or market positioning. Microsoft's steady, albeit less dramatic, growth indicates continued confidence in its cloud services (Azure), enterprise software, and AI initiatives.

The higher average daily volume for Apple suggests more active trading and potentially higher liquidity compared to Microsoft.

### Comparison vs Recent Trend

**Apple (AAPL)**

*   **Recent Trend:** Over the last few days of the 6-month period, AAPL experienced a significant spike (e.g., a jump from $245.50 on Sept 19 to $256.08 on Sept 22), followed by a slight dip. This indicates recent positive momentum, but also some profit-taking or minor consolidation.
*   **Volatility:** The daily percentage changes in Apple's stock price appear more pronounced in the last five trading days, indicating relatively higher recent volatility.

**Microsoft (MSFT)**

*   **Recent Trend:** MSFT has shown a relatively stable trend in its closing prices over the last five trading days, oscillating around the $510-$515 mark. There was a notable jump from Sept 18 ($508.45) to Sept 19 ($517.93).
*   **Volatility:** Microsoft's daily price movements in the last five trading days seem less volatile compared to Apple's, suggesting a more stable trading pattern.

### Risk-Aware Considerations

1.  **Past performance is not indicative of future results.** While AAPL has outperformed MSFT over the last six months, market conditions and company-specific factors can change rapidly.
2.  **Increased volatility can lead to greater price swings.** Apple's recent higher volatility could present both opportunities and risks for investors.
3.  **Diversification is crucial.** Concentrating investments in a few stocks, even leading ones like AAPL and MSFT, carries inherent risks. Investors should consider a diversified portfolio aligned with their risk tolerance and financial goals.
"""
