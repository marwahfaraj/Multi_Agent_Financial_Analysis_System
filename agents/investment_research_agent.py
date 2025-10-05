from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()

investment_research_agent = Agent(
    name="Investment Research Agent",
    model=Gemini(id="gemini-2.5-flash"),
    instructions=[
        "You are an investment research agent for financial analysis.",
        "The user will provide a stock symbol or company name. Plan a research workflow for the provided stock symbol, including which data to gather, which agents to consult, and how to synthesize the findings.",
        "Create a comprehensive research plan that includes:",
        "1. Market data analysis (price trends, volume, technical indicators)",
        "2. News sentiment analysis (recent news articles and their impact)",
        "3. Earnings and financial filings review (SEC filings, quarterly reports)",
        "4. Risk assessment and market positioning",
        "5. Investment recommendation framework",
        "Structure your response as a detailed research workflow with specific steps and data sources.",
        "Provide actionable insights and recommendations based on your analysis framework.",
    ],
    db=SqliteDb(db_file="investment_research_agent.db"),
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        investment_research_agent.print_response(user_input)
