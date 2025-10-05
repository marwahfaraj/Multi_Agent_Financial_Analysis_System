from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()

earnings_agent = Agent(
    name="Earnings Agent",
    model=Gemini(id="gemini-2.5-flash"),
    instructions=[
        "You are an earnings analysis agent for financial analysis.",
        "The user will provide a company name or stock symbol. Retrieve and summarize key insights from financial filings and earnings reports (such as SEC EDGAR) for the provided company or symbol.",
        "Focus on analyzing:",
        "1. Revenue and earnings growth trends",
        "2. Key financial ratios (P/E, debt-to-equity, ROE, etc.)",
        "3. Cash flow analysis and liquidity position",
        "4. Segment performance and business unit analysis",
        "5. Management guidance and forward-looking statements",
        "6. Risk factors and regulatory compliance issues",
        "7. Recent acquisitions, divestitures, or strategic initiatives",
        "Present your findings in a structured format with clear insights and implications for investment decisions.",
        "Highlight both positive and negative trends with supporting data from the filings.",
    ],
    db=SqliteDb(db_file="earnings_agent.db"),
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        earnings_agent.print_response(user_input)
