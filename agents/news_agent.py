from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agents.config import DEFAULT_AGENT_KWARGS

news_agent = Agent(
    name="News Agent",
    instructions=[
        "You are a financial analysis assistant."
        "The user will provide the name of a company or its stock ticker symbol. Please identify the most recent and relevant news articles for financial analysis.",
        "First search for recent news articles about the company or stock ticker symbol provided by the user.",
        "Then analyze the news articles and classify tem as positive, negative, or neutral in terms of their potential impact on the company's stock price.",
        "Create a pandas DataFrame to summarize the news articles, including these columns: 'Title', 'Source', 'URL', 'Date', 'Sentiment', and 'Summary'.",
        """Example of the DataFrame format:
        {
            'Title': 'Example News Article',
            'Source': 'Example News Source',
            'URL': 'https://example.com/news/article',
            'Date': '2023-01-01',
            'Sentiment': 'Positive',
            'Summary': 'This is an example summary of the news article.'
        }""",
        "Respond with a bullet point list of the DataFrame contents.",
    ],
    tools=[DuckDuckGoTools(fixed_max_results=5)],
    tool_call_limit=5,
    add_history_to_context=True,
    add_datetime_to_context=True,
    markdown=True,
    **DEFAULT_AGENT_KWARGS
)

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        news_agent.print_response(user_input)
