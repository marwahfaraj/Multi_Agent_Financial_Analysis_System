"""
Complete Workflow Implementation
Includes Prompt Chaining and Evaluator-Optimizer patterns
"""
from agno.workflow import Step, Workflow, StepInput, StepOutput, Parallel
from json import loads
from agents.preprocessing_agent import preprocessing_agent
from agents.investment_research_agent import investment_research_agent
from agents.memory_agent import memory_agent
from workflows.routing import multi_agent_routing


def parse_preprocessing_output(step_input: StepInput) -> dict:
    """
    Parses the JSON output from the preprocessing agent.

    Args:
        step_input: The step input containing preprocessing output

    Returns:
        dict: Parsed dictionary containing ticker, action_item, and data_types.
    """
    try:
        output = step_input.get_step_content("Preprocess Input")
        # Clean the output to ensure it's valid JSON
        cleaned_output = "\n".join(
            line for line in output.splitlines() if not line.strip().startswith("```")
        )
        return loads(cleaned_output)
    except Exception as e:
        print(f"Error parsing preprocessing output: {e}")
        return {}


def multi_agent_router_executor(step_input: StepInput) -> StepOutput:
    """
    Executor function to route tasks to multiple agents based on input parameters.

    Args:
        step_input (StepInput): Input containing content and agent types.

    Returns:
        StepOutput: Output from the routed agents.
    """
    data = parse_preprocessing_output(step_input)
    ticker = data.get("ticker")
    action_item = data.get("action_item")
    agent_types = data.get("data_types", [])

    # Call the multi-agent routing function with the provided content and agent types
    result = multi_agent_routing(f"Stock Ticker: {ticker}\n{action_item}", agent_types)
    output = ""
    for agent, response in result["responses"].items():
        output += f"{agent}: {response}\n\n"

    return StepOutput(content=output)


def stored_data_retriever_executor(step_input: StepInput) -> StepOutput:
    """
    Executor function to retrieve stored data from memory based on input parameters.

    Args:
        step_input (StepInput): Input containing content and agent types.

    Returns:
        StepOutput: Output from the memory agent.
    """
    data = parse_preprocessing_output(step_input)
    ticker = data.get("ticker")
    action_item = data.get("action_item")

    memory_prompt = "\n".join(
        [
            f"Retrieve any stored information related to {ticker} that might assist with the following request: {action_item}.",
            "This is what we already know, do not repeat it: ",
            step_input.previous_step_content,
            "If no relevant information is found, respond with 'No relevant information found.'",
        ]
    )
    memory_response = memory_agent.run(memory_prompt).content

    if "No relevant information found." not in memory_response:
        return StepOutput(
            content="\n".join(
                [
                    step_input.previous_step_content,
                    f"\n\nMemory Agent: {memory_response}",
                ]
            )
        )

    return StepOutput(content=step_input.previous_step_content)


workflow = Workflow(
    name="Analysis workflow",
    steps=[
        # Parse the user input to extract ticker, action item, and data types
        Step(name="Preprocess Input", agent=preprocessing_agent),
        # Gather data using the multi-agent router
        Step(
            name="Gather Data",
            executor=multi_agent_router_executor,
        ),
        # Retrieve any additional stored data from memory
        Step(
            name="Retrieve Stored Data",
            executor=stored_data_retriever_executor,
        ),
        # Synthesize the analysis and store relevant information in memory
        Parallel(
            Step(
                name="Synthesize Analysis",
                agent=investment_research_agent,
            ),
            Step(
                name="Store Data in Memory",
                agent=memory_agent,
            ),
        ),
    ],
)


if __name__ == "__main__":
    workflow.print_response(
        (
            "Analyze the financial health and market position of Apple "
            "based on recent earnings reports, market data, and news articles."
        ),
        stream=True,
        stream_intermediate_steps=True,
    )
