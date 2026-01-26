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
st.set_page_config(page_title="Varun's Intelligence Terminal", page_icon="🦁", layout="wide")
load_dotenv()

# --- 2. BACKEND: DATA & AI ---
# Initialize the "Brain"
llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))

def get_stock_data(ticker, period="6mo"):
    """Fetches historical data."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist
    except:
        return pd.DataFrame()

def get_portfolio_metrics(tickers):
    """
    Fetches price, change, and volatility for the portfolio.
    Returns a DataFrame ready for plotting.
    """
    data = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period="1mo") # 1 month for volatility
            if len(hist) > 1:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change_pct = ((curr - prev) / prev) * 100
                
                # Volatility (Standard Deviation of daily returns)
                daily_returns = hist['Close'].pct_change().dropna()
                volatility = daily_returns.std() * 100
                
                data.append({
                    "Ticker": t,
                    "Price": curr,
                    "Daily Change %": change_pct,
                    "Volatility (Risk)": volatility,
                    "Volume": hist['Volume'].iloc[-1]
                })
        except:
            pass
    return pd.DataFrame(data)

def portfolio_chat_agent(query, portfolio_df):
    """
    Context-aware chatbot that knows your portfolio data.
    """
    data_context = portfolio_df.to_string(index=False)
    prompt = (
        f"You are a financial portfolio assistant. Here is the user's real-time portfolio data:\n"
        f"{data_context}\n\n"
        f"User Query: {query}\n"
        f"Task: Answer the query briefly based strictly on the data above. "
        f"If asked for advice, suggest based on 'High Volatility' (Risk) vs 'Return' logic."
    )
    response = llm.invoke(prompt)
    return response.content

def deep_dive_analysis(ticker):
    """Deep dive research agent."""
    search = DuckDuckGoSearchRun()
    news = search.invoke(f"{ticker} stock news analysis buy sell hold")
    prompt = (
        f"Analyze {ticker} based on this news: {news}\n"
        f"Provide a 'Bull vs Bear' analysis and a final verdict."
    )
    return llm.invoke(prompt).content

# --- 3. FRONTEND UI ---

# Sidebar: Portfolio State
with st.sidebar:
    st.header("🦁 Portfolio Config")
    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL"]
    
    # Portfolio Editor
    user_tickers = st.text_area("Your Tickers", value=", ".join(st.session_state["portfolio"]))
    st.session_state["portfolio"] = [x.strip().upper() for x in user_tickers.split(",")]
    st.caption("Updates apply immediately.")

# Main App
st.title("Varun's Intelligence Terminal")
tab1, tab2 = st.tabs(["🛡️ Portfolio Guard (Chat & Charts)", "🔬 Deep Dive Research"])

# --- TAB 1: PORTFOLIO GUARD ---
with tab1:
    col_a, col_b = st.columns([2, 1])
    
    # A. The Data Engine
    with col_a:
        st.subheader("Market Pulse")
        with st.spinner("Scanning market data..."):
            df = get_portfolio_metrics(st.session_state["portfolio"])
            
            # 1. Performance Heatmap (Bar Chart)
            fig_perf = px.bar(
                df, x='Ticker', y='Daily Change %',
                color='Daily Change %',
                color_continuous_scale=['red', 'gray', 'green'],
                range_color=[-3, 3],
                title="Today's Performance"
            )
            st.plotly_chart(fig_perf, use_container_width=True)
            
            # 2. Risk vs Reward Scatter (The "Fancy" Chart)
            st.subheader("Risk vs. Reward Radar")
            st.caption("Top Left = Good (Low Risk, High Gain). Bottom Right = Bad (High Risk, Low Gain).")
            
            if not df.empty:
                fig_risk = px.scatter(
                    df, x='Volatility (Risk)', y='Daily Change %',
                    size='Price', color='Ticker', text='Ticker',
                    title="Volatility Analysis (Size = Stock Price)"
                )
                fig_risk.update_traces(textposition='top center')
                st.plotly_chart(fig_risk, use_container_width=True)

    # B. The Portfolio Chatbot
    with col_b:
        st.subheader("💬 Ask the Analyst")
        st.info("Ask about your portfolio (e.g., 'What should I sell?', 'Who is riskiest?')")
        
        # Initialize Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display Chat History
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Ask about your stocks..."):
            # 1. User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 2. AI Response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing portfolio data..."):
                    response = portfolio_chat_agent(prompt, df)
                    st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- TAB 2: DEEP DIVE (Research) ---
with tab2:
    st.subheader("Single Stock Research")
    t_input = st.text_input("Enter Ticker", value="AMZN").upper()
    
    if st.button("Analyze Stock"):
        with st.spinner("Fetching Bloomberg-level data..."):
            # Chart
            hist = get_stock_data(t_input)
            fig = go.Figure(data=[go.Candlestick(x=hist.index,
                open=hist['Open'], high=hist['High'],
                low=hist['Low'], close=hist['Close'])])
            st.plotly_chart(fig, use_container_width=True)
            
            # Analysis
            analysis = deep_dive_analysis(t_input)
            st.markdown(analysis)