import streamlit as st
import os
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun

# --- 1. SETUP & AUTH ---
st.set_page_config(page_title="Varun's Portfolio Guard", page_icon="🛡️", layout="wide")
load_dotenv()

# Simple Password Protection
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == os.getenv("APP_PASSWORD", "varun123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Access Code", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter Access Code", type="password", on_change=password_entered, key="password")
        st.error("😕 Access Denied")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- 2. BACKEND LOGIC ---
llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))

def fetch_portfolio_data(tickers):
    """
    Fetches Price AND Risk Data (Stress Testing).
    """
    data = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            # Fetch 1 month of history for Volatility calc
            hist = stock.history(period="1mo")
            
            if len(hist) >= 2:
                # Price Data
                close = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change_pct = ((close - prev_close) / prev_close) * 100
                
                # Risk Data (Simple Volatility Stress Test)
                # Calculate standard deviation of daily returns
                daily_returns = hist['Close'].pct_change().dropna()
                volatility = daily_returns.std() * 100 # In percentage
                
                # Risk Label
                if volatility > 2.5: risk_label = "🔥 High"
                elif volatility > 1.5: risk_label = "⚠️ Med"
                else: risk_label = "✅ Low"

                data.append({
                    "Ticker": t,
                    "Price": close,
                    "Change (%)": change_pct,
                    "Volatility (30d)": f"{volatility:.2f}%",
                    "Risk Level": risk_label
                })
        except:
            pass
    return pd.DataFrame(data)

def generate_morning_brief(portfolio_df):
    """
    AI synthesizes the 'Daily Digest' based on the data.
    """
    data_str = portfolio_df.to_string(index=False)
    prompt = (
        f"Here is my portfolio status today:\n{data_str}\n\n"
        f"Task: Write a 'Daily Executive Digest' for me (Varun). "
        f"1. Summarize the overall health (Green/Red). "
        f"2. Flag any stock with 'High' risk level and explain why volatility might be high (general knowledge). "
        f"3. Keep it professional, concise, and under 150 words."
    )
    response = llm.invoke(prompt)
    return response.content

def scout_opportunities(sector, strategy):
    """
    Scouts for new stocks based on Strategy (e.g., Growth vs Value).
    """
    search = DuckDuckGoSearchRun()
    query = f"top {strategy} stocks in {sector} sector to buy now news analysis"
    raw_news = search.invoke(query)
    
    prompt = (
        f"Based on this news search: {raw_news}\n"
        f"Task: Recommend 3 specific stocks that fit the '{strategy}' strategy in '{sector}'. "
        f"For each, provide: \n"
        f"1. Ticker\n"
        f"2. The 'Alpha' (Why it might grow)\n"
        f"3. One risk factor."
    )
    response = llm.invoke(prompt)
    return response.content

# --- 3. FRONTEND UI ---

# Sidebar: Portfolio Settings
with st.sidebar:
    st.header("💼 My Portfolio")
    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = ["AAPL", "NVDA", "TSLA", "MSFT"]
    
    portfolio_input = st.text_area(
        "Holdings (Comma Separated)", 
        value=", ".join(st.session_state["portfolio"])
    )
    st.session_state["portfolio"] = [x.strip().upper() for x in portfolio_input.split(",")]
    
    st.divider()
    st.caption(f"Logged in as: Varun")
    if st.button("Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

# Main Header
st.title("🛡️ Portfolio Guard AI")
st.markdown(f"**Welcome back, Varun.** Here is your daily intelligence briefing.")

# Tabs for different "Modes"
tab1, tab2 = st.tabs(["📊 Daily Digest & Health", "🔭 Opportunity Scout"])

with tab1:
    if st.button("🔄 Generate Daily Digest", type="primary"):
        with st.spinner("Analyzing market data and volatility..."):
            # 1. Fetch Data
            df = fetch_portfolio_data(st.session_state["portfolio"])
            
            # 2. AI Digest Section
            st.subheader("📝 Executive Morning Brief")
            digest = generate_morning_brief(df)
            st.info(digest)
            
            st.divider()
            
            # 3. The "Stress Test" Grid
            st.subheader("❤️ Portfolio Health Check")
            
            # Visual Risk Meter
            high_risk_count = len(df[df['Risk Level'].str.contains("High")])
            if high_risk_count > 0:
                st.warning(f"⚠️ Stress Alert: {high_risk_count} of your assets are showing high volatility today.")
            else:
                st.success("✅ Portfolio Stability: Healthy. No abnormal volatility detected.")

            # Data Table
            st.dataframe(
                df.style.map(lambda x: 'color: red' if 'High' in str(x) else 'color: green', subset=['Risk Level']),
                use_container_width=True
            )
            
            # Visual Performance
            st.subheader("Performance Map")
            fig = px.treemap(
                df, path=['Ticker'], values='Price',
                color='Change (%)',
                color_continuous_scale=['red', 'black', 'green'],
                range_color=[-3, 3]
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🔭 Find Your Next Winner")
    
    col1, col2 = st.columns(2)
    with col1:
        sector = st.selectbox("Sector", ["Artificial Intelligence", "Clean Energy", "BioTech", "FinTech", "Cybersecurity"])
    with col2:
        strategy = st.selectbox("Strategy", ["High Growth", "Undervalued / Dip", "Safe Dividend"])
        
    if st.button("Scout Opportunities"):
        with st.spinner(f"Scouting {sector} for {strategy} plays..."):
            report = scout_opportunities(sector, strategy)
            st.markdown(report)
            st.caption("⚠️ AI-generated research. Not financial advice.")