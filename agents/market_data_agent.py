# TODO: Atul - Market Data Agent
# This agent will be responsible for fetching market data using APIs
# Should integrate with tools/yahoo_finance_tools.py and other data sources
import json
import pandas as pd
import yfinance as yf

from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb
from agno.tools import tool

load_dotenv(".env")


@tool(name="fetch_quote", description="Get latest stock price and metadata for a symbol.")
def fetch_quote(symbol: str) -> str:
    """Fetch the latest quote for a stock symbol."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        price = info.last_price if hasattr(info, "last_price") else None
        if price is None:  # fallback to history
            hist = ticker.history(period="5d", interval="1d", auto_adjust=True)
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
        result = {
            "symbol": symbol,
            "last_price": price,
            "currency": getattr(info, "currency", None),
            "exchange": getattr(info, "exchange", None),
        }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"symbol": symbol, "error": str(e)})


@tool(name="fetch_ohlcv", description="Get last 5 OHLCV rows for a symbol.")
def fetch_ohlcv(symbol: str, period: str = "1y", interval: str = "1d") -> str:
    """Fetch OHLCV history for a stock symbol."""
    try:
        df = yf.download(
            symbol, period=period, interval=interval, progress=False, auto_adjust=True
        )
        if df.empty:
            return json.dumps({"symbol": symbol, "rows": 0, "ohlcv": []})
        tail = df.tail(5).reset_index()
        tail["Date"] = tail["Date"].astype(str)
        result = {
            "symbol": symbol,
            "rows": len(df),
            "period": period,
            "interval": interval,
            "tail5": tail.to_dict(orient="records"),
        }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"symbol": symbol, "error": str(e)})


TOOLS = [fetch_quote, fetch_ohlcv]

market_data_agent = Agent(
    name="Market Data Agent",
    model=Gemini(id="gemini-2.5-flash"),
    instructions=[
        "You are a financial market data agent.",
        "When the user provides a stock symbol or company name, call fetch_quote or fetch_ohlcv "
        "to fetch and summarize market data.",
        "Be clear about symbol, time range, and assumptions.",
    ],
    tools=TOOLS,
    db=SqliteDb(db_file="market_data_agent.db"),
    add_datetime_to_context=True,
    markdown=True,
)


if __name__ == "__main__":
    queries = [
        "Get the current price for TSLA",
        "Show OHLCV data for NVDA for the past month with daily interval"
    ]

    for q in queries:
        print(f"User: {q}")
        market_data_agent.print_response(q)
        print("-" * 40)

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        market_data_agent.print_response(user_input)