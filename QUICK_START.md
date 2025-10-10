# 🚀 Multi-Agent Financial Analysis System - Quick Start

## ⚡ Get Started in 30 Seconds

```bash
# Navigate to project directory
cd Multi_Agent_Financial_Analysis_System

# Start the system
python my_os.py
```

Your system is now running at **http://localhost:7777** 🎉

---

## 🌐 Access Your System

| Service | URL | Description |
|---------|-----|-------------|
| **Control Plane** | https://os.agno.com/ | Web UI for managing agents |
| **Local API** | http://localhost:7777 | Direct API access |
| **API Docs** | http://localhost:7777/docs | Interactive Swagger UI |
| **Configuration** | http://localhost:7777/config | System settings |

---

## 🤖 Your 6 Specialized Agents

1. **Preprocessing Agent** - Extracts ticker symbols and user intent
2. **Market Data Agent** - Fetches real-time stock prices (uses yfinance)
3. **News Agent** - Retrieves financial news (uses DuckDuckGo)
4. **Earnings Agent** - Analyzes earnings reports and SEC filings
5. **Memory Agent** - Stores information across sessions
6. **Investment Research Agent** - Synthesizes comprehensive analysis

---

## 💡 How to Use

### Option 1: Control Plane (os.agno.com) ✨ Recommended

1. **Go to:** https://os.agno.com/
2. **Sign in** with your account
3. **Your AgentOS should show as active** (green dot)
4. **Click "Chat"** in the left sidebar
5. **Select an agent** from the dropdown:
   - **Market Data Agent** → "Get current price for AAPL"
   - **News Agent** → "Latest news on Tesla"
   - **Investment Research Agent** → "Analyze Microsoft stock"

> ⚠️ **Important:** The Preprocessing Agent only extracts ticker info. Use other agents for actual analysis!

### Option 2: Local API Documentation

1. Open **http://localhost:7777/docs**
2. Click on any endpoint
3. Click "Try it out"
4. Fill in your query
5. Click "Execute"

### Option 3: Complete Workflow (Python)

```python
from workflows.workflow_implementation import workflow

# Run complete multi-agent analysis
workflow.print_response(
    "Analyze the financial health of Apple",
    stream=True
)
```

This runs all agents in sequence:
1. Preprocessing → Extracts ticker
2. Routing → Sends to Market/News/Earnings agents
3. Memory → Retrieves stored data
4. Investment Research → Synthesizes final report

### Option 4: Terminal API Calls

```bash
# Market data query
curl -X POST "http://localhost:7777/agents/market-data-agent/runs" \
  -F "message=Get current price for TSLA"

# News query
curl -X POST "http://localhost:7777/agents/news-agent/runs" \
  -F "message=Latest news on Microsoft"
```

---

## 🎯 Example Queries

Try these in the control plane or API:

| Query | Best Agent | What You Get |
|-------|------------|--------------|
| "Get current price for AAPL" | Market Data Agent | Real-time stock price & metadata |
| "Latest news on Tesla" | News Agent | Recent news with sentiment analysis |
| "Analyze Microsoft stock" | Investment Research Agent | Comprehensive investment analysis |
| "Amazon earnings report" | Earnings Agent | Financial ratios, revenue trends |

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional
NEWSAPI_KEY=your_newsapi_key_here
FRED_API_KEY=your_fred_api_key_here

# For Control Plane (already set)
AGNO_OS_KEY=OSK_Z8fFZqVhbErMBYDSFtua
```

### Agent Settings

- **Model:** Gemini 2.5 Flash (Google)
- **Retries:** 5 attempts
- **Backoff:** Exponential
- **Delay:** 5 seconds between retries

All configured in `agents/config.py`

---

## 🛑 Stop the System

```bash
# If running in terminal, press Ctrl+C

# Or kill the process
lsof -ti :7777 | xargs kill -9
```

---

## 📁 Project Structure

```
Multi_Agent_Financial_Analysis_System/
├── agents/                      # All agent definitions
│   ├── config.py               # Shared configuration
│   ├── preprocessing_agent.py  # Extracts ticker & intent
│   ├── market_data_agent.py    # Stock prices (yfinance)
│   ├── news_agent.py           # News search (DuckDuckGo)
│   ├── earnings_agent.py       # SEC filings analysis
│   ├── memory_agent.py         # Persistent memory
│   └── investment_research_agent.py  # Main orchestrator
├── workflows/                   # Workflow patterns
│   ├── workflow_implementation.py    # Complete pipeline
│   ├── routing.py              # Multi-agent routing
│   ├── prompt_chaining.py      # Sequential processing
│   └── evaluator_optimizer.py  # Quality improvement
├── my_os.py                    # AgentOS configuration
├── start_agentos.py            # Easy launcher script
├── notebook.ipynb              # Development notebook
├── requirements.txt            # Python dependencies
└── README.md                   # Project overview
```

---

## 🆘 Troubleshooting

### "Address already in use"
```bash
lsof -ti :7777 | xargs kill -9
python my_os.py
```

### "AgentOS not active" on control plane
1. Make sure `python my_os.py` is running
2. Click the "REFRESH" button on os.agno.com
3. Check terminal for errors

### "No module found" errors
```bash
pip install -r requirements.txt
```

### API returns empty response
- Check that agents are using the correct agent (not Preprocessing)
- View terminal logs for errors
- Verify API key in .env file

---

## 🎓 Understanding Agent Roles

### Preprocessing Agent
- **Purpose:** Parse user input
- **Output:** JSON with ticker, action, data_types
- **Use Case:** First step in workflow
- ⚠️ **Does NOT provide analysis** - only extracts information

### Market Data Agent  
- **Purpose:** Get stock prices
- **Tools:** fetch_quote, fetch_ohlcv (yfinance)
- **Use Case:** "What's the price of AAPL?"

### News Agent
- **Purpose:** Find financial news
- **Tools:** DuckDuckGo search
- **Use Case:** "Latest news on Tesla"

### Earnings Agent
- **Purpose:** Analyze financial reports
- **Output:** Revenue trends, ratios, guidance
- **Use Case:** "Amazon earnings analysis"

### Memory Agent
- **Purpose:** Store/retrieve past analysis
- **Tools:** add_memory, get_memories
- **Use Case:** "What do I know about Google?"

### Investment Research Agent
- **Purpose:** Orchestrate comprehensive analysis
- **Output:** Complete investment recommendation
- **Use Case:** "Should I invest in Microsoft?"

---

## 🚀 Next Steps

### 1. Test Individual Agents
Use the control plane or /docs to test each agent

### 2. Run Complete Workflow
Use `workflow_implementation.py` for end-to-end analysis

### 3. Build Custom Frontend
Your API at localhost:7777 is ready for any UI

### 4. Deploy to Production
Deploy to AWS, GCP, Azure, or other cloud platforms

### 5. Monitor with Control Plane
Use os.agno.com for analytics and team collaboration

---

## 📊 System Info

- **Name:** Multi-Agent Financial system
- **OS ID:** financial-analysis-os
- **Endpoint:** http://localhost:7777
- **Version:** 1.0.0
- **Agents:** 6 specialized agents
- **Model:** Gemini 2.5 Flash
- **Status:** ✅ Active

---

## 💡 Pro Tips

1. **Use Investment Research Agent** for comprehensive analysis, not Preprocessing
2. **Keep terminal open** when running `python my_os.py`
3. **Check /docs** to see all available endpoints
4. **Use workflows** for complex multi-step analysis
5. **Control plane** provides the best user experience

---

## 📚 Additional Resources

- **Local API Docs:** http://localhost:7777/docs
- **Control Plane:** https://os.agno.com/
- **Agno Documentation:** https://docs.agno.com/
- **Project README:** See README.md for detailed information

---

**Your Multi-Agent Financial Analysis System is ready to use! 🎊**

Start with: `python my_os.py`

Then visit: https://os.agno.com/ and select **Market Data Agent** or **Investment Research Agent** for actual analysis!
