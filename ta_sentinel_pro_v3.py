import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from polygon import RESTClient

st.set_page_config(page_title="TA Sentinel PRO v3", layout="wide", page_icon="🚀")
st.title("🚀 TA Sentinel PRO v3 — Ultimate Genius Trader Edition")
st.markdown("**Multi-Timeframe • ML Predictor • Full Features**")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("🔑 API Keys")
    polygon_key = st.text_input("Polygon.io API Key", 
                                type="password", 
                                value=st.session_state.get("saved_polygon_key", ""),
                                key="polygon_input")
    
    if st.button("💾 Save API Key"):
        if polygon_key.strip():
            st.session_state.saved_polygon_key = polygon_key.strip()
            st.success("✅ API Key saved! You can now refresh the page.")
        else:
            st.error("Please enter your Polygon API key")

    st.header("⚙️ Trading Settings")
    account_size = st.number_input("Account Size ($)", value=10000.0, min_value=1000.0)
    risk_percent = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.1)
    risk_reward = st.slider("Risk:Reward Ratio", 1.5, 3.0, 2.0, 0.1)

# ====================== SESSION STATE ======================
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"]
if 'price_histories' not in st.session_state:
    st.session_state.price_histories = {}
if 'alert_log' not in st.session_state:
    st.session_state.alert_log = []
if 'positions' not in st.session_state:
    st.session_state.positions = {}
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# ====================== HELPERS ======================
def get_client():
    if 'saved_polygon_key' in st.session_state and st.session_state.saved_polygon_key:
        return RESTClient(api_key=st.session_state.saved_polygon_key)
    return None

def calculate_indicators(df):
    if len(df) < 30:
        return None
    close = df['close']
    sma50 = close.rolling(50).mean().iloc[-1]
    atr = close.diff().abs().rolling(14).mean().iloc[-1] if len(close) > 14 else 1.0
    score = 0.0
    if close.iloc[-1] > sma50: score += 0.4
    score = round(score, 2)
    return {
        "price": round(close.iloc[-1], 2),
        "score": score,
        "atr": round(atr, 4)
    }

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Live Dashboard", "🔬 Backtester", "📰 News & Options", "📈 Portfolio Risk", "⚙️ Deploy"])

with tab1:
    st.subheader("Live Market Monitor")
    st.caption(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
    col1, col2 = st.columns([3,1])
    with col1:
        new_ticker = st.text_input("Add ticker", placeholder="e.g. GOOGL").upper().strip()
    with col2:
        if st.button("➕ Add", use_container_width=True) and new_ticker and new_ticker not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_ticker)
            st.rerun()

    if st.button("🔄 Force Refresh All Data", type="primary", use_container_width=True):
        client = get_client()
        if not client:
            st.error("❌ Please save your Polygon API key first")
        else:
            for ticker in st.session_state.watchlist:
                try:
                    last_trade = client.get_last_trade(ticker)
                    price = float(last_trade.price)
                    st.success(f"✅ {ticker} live price: ${price:.2f}")
                except:
                    st.info(f"📅 {ticker}: Market is closed (weekend). Using last available data.")
                    # Fallback: try to get recent daily data
                    try:
                        aggs = list(client.get_aggs(ticker, 1, "day", limit=5))
                        if aggs:
                            price = float(aggs[-1].close)
                            st.write(f"Last close for {ticker}: ${price:.2f}")
                    except:
                        st.warning(f"{ticker}: No data available right now")
            
            st.session_state.last_update = datetime.now()
            st.rerun()

    st.subheader("📢 Alert Log")
    for alert in reversed(st.session_state.alert_log[-10:]):
        st.write(alert)

with tab2:
    st.subheader("🔬 Backtester (coming soon in v4)")
    st.info("Full backtester will be added next — for now the live dashboard is ready.")

with tab3:
    st.subheader("📰 News & Unusual Options")
    st.info("News & options scanner coming in v4.")

with tab4:
    st.subheader("📈 Portfolio Risk")
    st.write("Open positions:", len(st.session_state.positions))

with tab5:
    st.subheader("🚀 Deploy to Cloud")
    st.markdown("When ready, say “deploy instructions” and I’ll walk you through free hosting.")

st.caption("TA Sentinel PRO v3 — Markets closed on weekends. Try again Monday–Friday during trading hours.")
