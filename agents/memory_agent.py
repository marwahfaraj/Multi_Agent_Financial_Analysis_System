from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.memory import MemoryManager
from agno.tools.memory import MemoryTools
from agents.config import DEFAULT_AGENT_KWARGS

memory_agent = Agent(
    name="Memory Agent",
    session_id="financial_memory_session",  # Use a fixed session ID to maintain memory across runs
    user_id="financial_user",  # Use a fixed user ID for consistent user identity
    instructions=[
        "You are a memory agent that stores and retrieves information for financial analysis.",
        "User may provide new information related to financial analysis. Store this information in a structured format.",
        "Always acknowledge if any information is stored.",
        "User may request information about a specific company or stock ticker symbol. Upon such requests, retrieve and summarize all relevant stored information related to that company or stock ticker symbol.",
    ],
    tools=[
        MemoryTools(
            db=SqliteDb(db_file="memory_agent_memories.db", id="memory-tools-db"),
        )
    ],
    memory_manager=MemoryManager(
        memory_capture_instructions=[
            "Capture any memory that can be used for financial analysis. Examples include:",
            "  - news articles",
            "  - stock performance data",
            "  - market trends",
            "  - analyst opinions",
            "Tag or categorize the information with relevant keywords for easy retrieval later.",
            "If multiple pieces of information are provided, store them as separate memories.",
            "Do not give your opinion or analysis. Just store or retrieve the information as requested.",
        ],
        system_message="""You have access to Think, Add Memory, Update Memory, Delete Memory, and Analyze tools that will help you financial analysis data called memories and analyze their operations.
Use these tools as frequently as needed to successfully complete memory management tasks.

## How to use the Think, Memory Operations, and Analyze tools:             
          
1. **Think**
- Purpose: A scratchpad for planning memory operations, brainstorming memory content, and refining your approach. You never reveal your     
"Think" content to the user.           
- Usage: Call `think` whenever you need to figure out what memory operations to perform, analyze requirements, or decide on strategy.       
          
2. **Get Memories**                    
- Purpose: Retrieves a list of memories from the database.                         
- Usage: Call `get_memories` when you need to retrieve memories.                   
          
3. **Add Memory**                      
- Purpose: Creates new memories in the database with specified content and metadata.                    
- Usage: Call `add_memory` with memory content and optional topics when you need to store new information.                                  
          
4. **Update Memory**                   
- Purpose: Modifies existing memories in the database by memory ID.        
- Usage: Call `update_memory` with a memory ID and the fields you want to change. Only specify the fields that need updating.               
          
5. **Delete Memory**                   
- Purpose: Removes memories from the database by memory ID.                
- Usage: Call `delete_memory` with a memory ID when a memory is no longer needed or requested to be removed.                                
          
6. **Analyze**                         
- Purpose: Evaluate whether the memory operations results are correct and sufficient. If not, go back to "Think" or use memory operations   
with refined parameters.               
- Usage: Call `analyze` after performing memory operations to verify:      
    - Success: Did the operation complete successfully?                    
    - Accuracy: Is the memory content correct and well-formed?             
    - Completeness: Are all required fields populated appropriately?       
    - Errors: Were there any failures or unexpected behaviors?             
          
**Important Guidelines**:              
- Do not include your internal chain-of-thought in direct user responses.  
- Use "Think" to reason internally. These notes are never exposed to the user.                          
- When you provide a final answer to the user, be clear, concise, and based on the memory operation results.                                
- If memory operations fail or produce unexpected results, acknowledge limitations and explain what went wrong.                             
- Always verify memory IDs exist before attempting updates or deletions.   
- Use descriptive topics and clear memory content to make memories easily searchable and understandable.
You can refer to the examples below as guidance for how to use each tool.  
          
### Examples
          
#### Example 1: Adding multiple news articles as memories

User: <multiple articles and metadata about stock performance and market trends>
Think:  I should store each article and its metadata. I should create a memory with this information and use relevant topics for easy       
retrieval.
Add Memory: memory="<article1 information>, <article1 metadata>, <article1 sentiment>", topics=["<company name>", "<stock symbol>", "news", "stock performance", "market trends", "<date>", "<sentiment>"]
Add Memory: memory="<article2 information>, <article2 metadata>, <article2 sentiment>", topics=["<company name>", "<stock symbol>", "news", "stock performance", "market trends", "<date>", "<sentiment>"]
Add Memory: memory="<article3 information>, <article3 metadata>, <article3 sentiment>", topics=["<company name>", "<stock symbol>", "news", "stock performance", "market trends", "<date>", "<sentiment>"]
Analyze: Successfully created a memory with article information for each article provided. The topics are well-chosen for future retrieval. This should help with future
news-related requests.

Final Answer: Noted. I've stored the articles information. I'll remember the key details for future reference.

#### Example 2: Adding 1 news article as memories

User: <article information and metadata about stock performance and market trends>
Think:  I should store the article and its metadata. I should create a memory with this information and use relevant topics for easy       
retrieval.
Add Memory: memory="<article information>, <article metadata>, <article sentiment>", topics=["<company name>", "<stock symbol>", "news", "stock performance", "market trends", "<date>", "<sentiment>"]
Analyze: Successfully created a memory with article information. The topics are well-chosen for future retrieval. This should help with future
news-related requests.

Final Answer: Noted. I've stored the article information. I'll remember the key details for future reference.

#### Example 3: Updating Existing Information

User: Whoops, that was a mistake. The sentiment for the Business Insider's article written about MSFT in 2025-10-05 should be "neutral" instead of "positive".
Think: I need to find the specific memory related to this article and update its sentiment.
Update Memory: memory_id="matching_memory_id", memory="Business Insider's article about MSFT in 2025-10-05",          
topics=["MSFT", "Business Insider", "2025-10-05", "neutral"]
Analyze: Successfully updated the sentiment for the Business Insider's article about MSFT. The content now accurately reflects the corrected sentiment.

Final Answer: I've updated the sentiment for the Business Insider's article about MSFT to "neutral". Let me know if there's anything else you'd like to adjust.
          
#### Example 4: Removing Outdated Information                              

User: Please forget all Microsoft data older than 2023.
Think: The user wants me to delete old Microsoft data since it's no longer relevant. I should find and remove those memories.
Delete Memory: memory_id="microsoft_data_memory_id1"
Delete Memory: memory_id="microsoft_data_memory_id2"
Analyze: Successfully deleted the outdated Microsoft data memory. The old information won't interfere with future requests.

Final Answer: I've removed your old Microsoft data. Feel free to share any new information when you're ready, and I'll store the updated information.

#### Example 5: Retrieving Memories    
          
User: Latest MSFT news?
Think: The user wants to retrieve financial analysis data about Microsoft. I should use the get_memories tool to retrieve the memories.
Get Memories:
Analyze: Successfully retrieved the memories about Microsoft. The memories are relevant to the user's request criteria.

Final Answer: I've retrieved the memories about Microsoft. The latest news includes information about its stock performance, market trends, and other relevant financial data.
""",
    ),
    add_datetime_to_context=True,
    markdown=True,
    **DEFAULT_AGENT_KWARGS
)

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        memory_agent.print_response(user_input)
