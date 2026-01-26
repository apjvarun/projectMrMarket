# 🦁 Mr. Market's Intelligent Terminal

**A GenAI-Powered Financial Intelligence Platform for the Modern Investor.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red) ![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange) ![LangChain](https://img.shields.io/badge/Orchestration-LangChain-green)

Mr. Market is a "Bloomberg Terminal Lite" designed for busy professionals. Unlike standard stock trackers that only show prices, this application uses **Agentic RAG (Retrieval-Augmented Generation)** to act as a 24/7 financial analyst. It combines real-time data visualization with a context-aware chatbot that intelligently routes queries between live web data, personal portfolio context, and general financial concepts.

---

## 🎯 Product Vision

**The Problem:** Moderate investors face "Information Overload." General news feeds are too broad, and professional terminals are too complex/expensive.
**The Solution:** A focused, AI-driven dashboard that filters noise and provides actionable insights tailored to the user's specific holdings.

### User Persona
* **The Busy Professional:** Has capital but no time. Needs synthesis ("Why is my portfolio down?"), not just raw data points.
* **Goal:** Tracking, Risk Management, and Discovery without the friction of traditional tools.

---

## 🚀 Key Features

### 1. 🌍 Market Deck (The "Morning Brief")
* **Global Pulse:** Real-time tracking of major indices (S&P 500, Nasdaq, Bitcoin).
* **AI News Curator:** Instead of a flood of links, the Agent reads the web and extracts exactly the **Top 5 Critical Headlines** for the day, stripped of noise and formatted for 30-second consumption.

### 2. 🛡️ Portfolio Guard (The "Risk Engine")
* **Risk Radar:** A Scatter Plot visualization analyzing **Volatility (Risk) vs. Returns**. This helps users instantly identify "High Risk / Low Reward" assets in their portfolio.
* **Performance Heatmap:** A visual breakdown of daily gainers and losers.

### 3. 💬 Universal Financial Chatbot (Router Agent)
A dual-brain agent that breaks the limitations of standard chatbots. It uses a **Router Architecture** to decide how to answer:
* *Context:* "How is **my** Apple stock doing?" $\rightarrow$ Queries User's Real-time DataFrame.
* *Live Search:* "What is the current inflation rate?" $\rightarrow$ Triggers DuckDuckGo Search.
* *Tutor Mode:* "Explain 'Short Selling' like I'm 5." $\rightarrow$ Uses Internal LLM Knowledge.

### 4. 🔬 Intelligent Research (Natural Language Search)
* **Smart Ticker Resolution:** Users think in brands, not tickers. You can type **"The company that owns Instagram"** and the AI resolves it to **META** before fetching data.
* **Deep Dive Analysis:** Generates a "Moderate Investor" report focusing on **Analyst Consensus** and **Price Targets** rather than just raw technicals.

---

## 🛠️ Technical Architecture

This project utilizes a **Retrieval-Augmented Generation (RAG)** approach.

* **Frontend:** [Streamlit](https://streamlit.io/) (for rapid UI prototyping).
* **LLM Engine:** [Google Gemini 1.5 Flash](https://deepmind.google/technologies/gemini/) (chosen for low latency and high context window).
* **Orchestration:** [LangChain](https://python.langchain.com/) (managing prompts and tools).
* **Data Layer:**
    * `yfinance`: Real-time market data.
    * `DuckDuckGo`: Live web search tool.
    * `Pandas`: Data manipulation and volatility calculations.
    * `Plotly`: Interactive financial charting.

---

## ⚙️ Installation & Setup

### Prerequisites
* Python 3.10 or higher.
* A Google Cloud API Key (Gemini).

### 1. Clone the Repository
```bash
git clone [https://github.com/apjvarun/projectMrMarket.git](https://github.com/apjvarun/projectMrMarket.git)
cd projectMrMarket
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Secrets
```bash
GOOGLE_API_KEY="AIzaSy... (Your Google Gemini Key)"
GEMINI_MODEL="gemini-2.5-flash"
```

### 4. Run the App
```bash
streamlit run streamlit_app.py
```

### 5. Project Structure
```bash
├── streamlit_app.py      # Main application logic (Frontend + Agent Router)
├── requirements.txt      # Dependencies (yfinance, langchain, plotly, etc.)
├── .env                  # API Keys (Excluded from Version Control)
└── README.md             # Product Documentation
```

## Author
* Varun Gupta [https://www.linkedin.com/in/varun-gupta10/](LinkedIn)
* Product Manager & AI Strategist
* Building at the intersection of Product Strategy and Agentic Workflows.
