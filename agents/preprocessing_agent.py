from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()

preprocessing_agent = Agent(
    name="Preprocessing agent",
    model=Gemini(id="gemini-2.5-flash"),
    instructions=[
        "You are a financial analysis assistant."
        "Your task is to preprocess prompt inputs for downstream analysis.",
        "You respond in strict JSON format.",
        "Given raw text input, perform the following preprocessing steps:",
        "- Identify the ticker symbol for the company mentioned in the text.",
        "- Extract the intent of the user's request without losing context. Convert it into a concise action item.",
        "- Determine the type of data needed for analysis (The only valid values are: ['earnings', 'news', 'market']).",
        "Examples:",
        """Input: "Can you provide the latest news on Microsoft?"
Output: {"ticker": "MSFT", "action_item": "Provide the latest news on Microsoft", "data_types": ["news"]}""",
        """Input: "I need the recent earnings report for Apple."
Output: {"ticker": "AAPL", "action_item": "Retrieve the recent earnings report for Apple", "data_types": ["earnings"]}""",
        """Input: "What's the current market status of Tesla?"
Output: {"ticker": "TSLA", "action_item": "Get the current market status of Tesla", "data_types": ["market"]}""",
        """Input: "Perform a comprehensive analysis of Amazon.",
Output: {"ticker": "AMZN", "action_item": "Perform a comprehensive analysis of Amazon", "data_types": ["earnings", "news", "market"]}""",
    ],
    use_json_mode=True
)

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        preprocessing_agent.print_response(user_input)
