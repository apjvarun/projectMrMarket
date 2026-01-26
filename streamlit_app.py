import streamlit as st
import os
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Mr. Market's Intelligence Terminal", page_icon="🦁", layout="wide")
load_dotenv()

# --- 2. BACKEND: INTELLIGENT AGENTS ---
llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))

def resolve_ticker(user_input):
    """Smart Search: 'iPhone company' -> 'AAPL'."""
    if len(user_input) < 6 and " " not in user_input:
        return user_input.upper()
    prompt = f"Return ONLY the stock ticker for '{user_input}'. If unclear, return 'INVALID'."
    result = llm.invoke(prompt).content.strip()
    return result if "INVALID" not in result else None

def get_stock_data(ticker, period="6mo"):
    try:
        return yf.Ticker(ticker).history(period=period)
    except:
        return pd.DataFrame()

def get_portfolio_metrics(tickers):
    """Calculates performance and risk for the dashboard."""
    data = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period="1mo")
            if len(hist) > 1:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change_pct = ((curr - prev) / prev) * 100
                volatility = hist['Close'].pct_change().dropna().std() * 100
                data.append({
                    "Ticker": t, "Price": curr, "Daily Change %": change_pct, 
                    "Volatility": volatility
                })
        except:
            pass
    return pd.DataFrame(data)

def get_general_market_news():
    """Fetches top 5 global financial headlines."""
    search = DuckDuckGoSearchRun()
    # 1. Broad search for today's top stories
    raw_results = search.invoke("top financial stock market news headlines today marketwatch bloomberg cnbc")
    
    # 2. Strict Formatting Prompt
    prompt = (
        f"Source Data: {raw_results}\n\n"
        f"Task: Extract exactly the Top 5 most critical market news headlines for today. "
        f"Format the output as a clean numbered list (1. [Headline] - [Brief Impact]). "
        f"Do not add any intro or outro text. Just the list."
    )
    return llm.invoke(prompt).content

def universal_financial_agent(query, portfolio_df):
    """
    The General Purpose Brain.
    Decides: Portfolio Data? Live Search? or General Concept?
    """
    search = DuckDuckGoSearchRun()
    portfolio_context = portfolio_df.to_string(index=False) if not portfolio_df.empty else "No portfolio data."
    
    # Step 1: Decision - Does this require live web search?
    router_prompt = (
        f"Query: '{query}'\n"
        f"Determine if this query requires LIVE external data (e.g. 'current inflation', 'news on X') "
        f"OR if it is a concept/portfolio question I can answer with current context. "
        f"Return ONLY 'SEARCH' or 'ANSWER'."
    )
    decision = llm.invoke(router_prompt).content.strip().upper()
    
    external_info = ""
    if "SEARCH" in decision:
        external_info = f"LIVE WEB SEARCH RESULTS: {search.invoke(query)}"
        
    # Step 2: Final Answer Generation
    final_prompt = (
        f"You are a Senior Financial Expert & Tutor. \n"
        f"User Query: {query}\n\n"
        f"--- SOURCES ---\n"
        f"1. User's Portfolio Data: {portfolio_context}\n"
        f"2. Live Web Data: {external_info}\n"
        f"----------------\n"
        f"Task: Answer the user's question. \n"
        f"- If about their portfolio, use Source 1.\n"
        f"- If about current market events, use Source 2.\n"
        f"- If a general concept (e.g. 'What is an ETF?'), explain it clearly using your own knowledge.\n"
        f"Keep the tone professional and educational."
    )
    
    return llm.invoke(final_prompt).content

def deep_dive_analysis(ticker):
    """Research Agent."""
    search = DuckDuckGoSearchRun()
    news = search.invoke(f"{ticker} stock analyst ratings price target news")
    prompt = (
        f"Analyze {ticker} based on this news: {news}\n"
        f"Provide: 1. Sentiment Summary 2. Analyst Consensus (Buy/Sell) 3. Key Risks."
    )
    return llm.invoke(prompt).content

# --- 3. FRONTEND UI ---

# Sidebar
with st.sidebar:
    st.header("🦁 Settings")
    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = ["AAPL", "NVDA", "TSLA", "MSFT"]
    
    user_tickers = st.text_area("My Portfolio", value=", ".join(st.session_state["portfolio"]))
    st.session_state["portfolio"] = [x.strip().upper() for x in user_tickers.split(",")]

# Main App
st.title("Mr. Market's Intelligence Terminal")
tab_market, tab_port, tab_research = st.tabs(["🌍 Market & News", "🛡️ Portfolio & Chat", "🔬 Deep Dive"])

# --- TAB 1: MARKET DECK ---
with tab_market:
    st.subheader("Global Pulse")
    c1, c2, c3 = st.columns(3)
    c1.metric("S&P 500", "Live", "Tracking")
    c2.metric("Nasdaq", "Live", "Tracking") 
    c3.metric("Bitcoin", "Live", "Tracking")
    
    st.divider()
    
    # Top News Feed
    col_news_a, col_news_b = st.columns([2, 1])
    with col_news_a:
        st.subheader("📰 Top 5 Market Headlines")
        
        # Use session state to keep news visible after other interactions
        if "market_news" not in st.session_state:
            st.session_state["market_news"] = None

        if st.button("🔄 Refresh Top 5 News", type="primary"):
            with st.spinner("Curating top stories from the web..."):
                news_list = get_general_market_news()
                st.session_state["market_news"] = news_list
        
        # Display the news if it exists in memory
        if st.session_state["market_news"]:
            st.markdown(st.session_state["market_news"])
            st.caption(f"Last updated: Just now")
        else:
            st.info("Click 'Refresh' to grab the latest top 5 stories.")
            
    with col_news_b:
        st.info("💡 Tip: Use the 'Portfolio & Chat' tab to ask ANY finance question.")

# --- TAB 2: PORTFOLIO & GENERAL CHAT ---
with tab_port:
    col_a, col_b = st.columns([2, 1])
    
    # Left: The Data
    with col_a:
        st.subheader("My Assets")
        df = get_portfolio_metrics(st.session_state["portfolio"])
        if not df.empty:
            fig = px.bar(df, x='Ticker', y='Daily Change %', color='Daily Change %', 
                         color_continuous_scale=['red', 'gray', 'green'], range_color=[-3, 3])
            # FIX: Replaced use_container_width with width="stretch"
            st.plotly_chart(fig, width="stretch")
            
            # Risk Radar
            fig_risk = px.scatter(df, x='Volatility', y='Daily Change %', size='Price', color='Ticker', title="Risk Radar")
            # FIX: Replaced use_container_width with width="stretch"
            st.plotly_chart(fig_risk, width="stretch")

    # Right: The Universal Chatbot
    with col_b:
        st.subheader("💬 Financial Advisor")
        st.caption("Ask ANYTHING: 'How are my stocks?', 'What is the Fed Rate?', 'Explain Options'.")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display history
        for msg in st.session_state.chat_history:
            st.chat_message(msg["role"]).write(msg["content"])

        # Input
        if prompt := st.chat_input("Ask your financial question..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            with st.spinner("Analyzing..."):
                reply = universal_financial_agent(prompt, df)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.chat_message("assistant").write(reply)

# --- TAB 3: SMART DEEP DIVE ---
with tab_research:
    st.subheader("🔬 Intelligent Research")
    query_input = st.text_input("Search Company", placeholder="e.g. 'The owner of Snapchat'")
    
    if st.button("Analyze") and query_input:
        with st.spinner("Resolving..."):
            ticker = resolve_ticker(query_input)
            if ticker:
                st.success(f"Identified: {ticker}")
                hist = get_stock_data(ticker)
                if not hist.empty:
                    st.metric(f"{ticker} Price", f"${hist['Close'].iloc[-1]:.2f}")
                    fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], close=hist['Close'], high=hist['High'], low=hist['Low'])])
                    # FIX: Replaced use_container_width with width="stretch"
                    st.plotly_chart(fig, width="stretch")
                    st.markdown(deep_dive_analysis(ticker))
            else:
                st.error("Could not find ticker.")