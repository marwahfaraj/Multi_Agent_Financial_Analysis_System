# Multi-Agent Financial Analysis System

<p align="center">
  <img src="image/multi_agent_sys.png" alt="Multi-Agent System Diagram" width="500"/>
</p>

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)

---

## 🚀 Overview
FData is a modern, agentic AI-powered platform for investment research and financial analysis. It simulates the operational architecture of modern AI-enabled hedge funds and investment platforms, using multiple specialized agents to analyze market and company performance, news, and filings, and to generate actionable investment insights.

---

## 🧩 Agent Architecture
- **Investment Research Agent:** Plans research workflow for a given stock symbol.
- **Market Data Agent:** Retrieves and analyzes time-series data (yfinance).
- **News Agent:** Retrieves, cleans, classifies, and summarizes financial news (NewsAPI, sentiment analysis, NER).
- **Earnings Agent:** Extracts and summarizes insights from financial filings and earnings reports (SEC EDGAR).
- **Evaluator Agent:** Critiques outputs, assesses coherence, and suggests improvements (LLM-based feedback loop).
- **Memory Agent:** Maintains lightweight memory of prior analyses for incremental learning.

---

## 🔄 Workflow Patterns
- **Prompt Chaining:** Ingest News → Clean Text → Classify Sentiment → Extract Entities → Summarize Content
- **Task Routing:** Dynamically route content to the appropriate agent (market/news/earnings)
- **Evaluator–Optimizer:** Evaluator agent critiques and origin agent refines output

---

## 🛠️ Technical Stack
**Programming Language:** Python 3.10+

**APIs & Data Sources:**
- Yahoo Finance (`yfinance`)
- NewsAPI.org (or Kaggle financial news datasets)
- FRED (Federal Reserve Economic Data)
- SEC EDGAR (Earnings Reports)

**Libraries/Frameworks:**
- pandas, matplotlib, scikit-learn
- openai, langchain, transformers
- nltk, spaCy
- streamlit (web UI)

**Version Control:** GitHub
**Documentation:** PEP8-compliant code, inline comments, comprehensive README

---

## ✨ Features
- 🤖 Modular, specialized agents for each analytical function
- 🔗 Chained prompts and agent workflows
- 📈 Real-time and historical data analysis
- 📰 News sentiment and entity extraction
- 🧠 Self-improving, memory-enabled agent design
- 📊 Modern Streamlit dashboard UI

---

## 🛠️ Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/your-repo.git
   cd your-repo
   ```
2. **Install dependencies**
   ```bash
   conda create -n aai520-mafas python=3.13 -y
   conda activate aai520-mafas
   pip install -r requirements.txt
   ```
3. **Download NLTK and spaCy models**
   ```python
   python -m nltk.downloader punkt vader_lexicon
   python -m spacy download en_core_web_sm
   ```
4. **Set your API keys** (for NewsAPI and OpenAI)
   ```bash
   export NEWSAPI_KEY=your_newsapi_key
   export OPENAI_API_KEY=your_openai_key
   export GOOGLE_API_KEY=your_google_aistudio_key
   ```
5. **Run the Streamlit app**
   ```bash
   streamlit run streamlit_app.py
   ```
6. **Or launch the Jupyter Notebook**
   ```bash
   jupyter notebook Investment_Research_Agent.ipynb
   ```

---

## 📦 Deliverables
- Main code and documentation in `Investment_Research_Agent.ipynb`
- Modern Streamlit app in `streamlit_app.py`
- Export notebook as PDF or HTML for submission
- [MIT License](LICENSE)

---

## 👥 Authors
- Marwah Faraj
- Atul Prasad
- Patrick Woo-Sam

---

## 📚 References
- Yahoo Finance, NewsAPI, Alpha Vantage, FRED, SEC EDGAR
- [PEP8 Style Guide](https://peps.python.org/pep-0008/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [NLTK Documentation](https://www.nltk.org/)
- [spaCy Documentation](https://spacy.io/)
- [LangChain](https://python.langchain.com/)
- [Transformers](https://huggingface.co/docs/transformers/index)

---

<p align="center">
  <em>AAI-520 Final Team Project &mdash; University of San Diego</em>
</p>
