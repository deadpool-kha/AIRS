"""
agents/quant.py

Quant Agent: Numerical analysis of market data.

Design decisions:
- Pure Python/pandas. No LLM. Calculations must be deterministic.
- Every metric has a docstring explaining what it means financially.
- Confidence drops if data is insufficient (< 30 days).
- Returns structured dict for easy consumption by other agents.

Financial concepts:
- Volatility: Higher = riskier. Annualized to compare across timeframes.
- Momentum: Positive = uptrend, negative = downtrend.
- Drawdown: Maximum loss from peak. 0.20 = you lost 20% at worst.
- Moving averages: Price above MA = bullish, below = bearish.
"""

import pandas as pd
import numpy as np


def calculate_returns(df: pd.DataFrame) -> dict:
    """
    Calculates daily, weekly, and monthly returns.
    
    Returns:
        Dict with return percentages.
    """
    # Daily return: (today - yesterday) / yesterday
    daily_returns = df["Close"].pct_change().dropna()
    
    # Weekly: approximate using 5 trading days
    weekly_return = (df["Close"].iloc[-1] / df["Close"].iloc[-5] - 1) if len(df) >= 5 else None
    
    # Monthly: approximate using 21 trading days
    monthly_return = (df["Close"].iloc[-1] / df["Close"].iloc[-21] - 1) if len(df) >= 21 else None
    
    return {
        "daily_mean": round(daily_returns.mean() * 100, 4),  # % format
        "daily_std": round(daily_returns.std() * 100, 4),
        "weekly": round(weekly_return * 100, 2) if weekly_return else None,
        "monthly": round(monthly_return * 100, 2) if monthly_return else None,
    }


def calculate_volatility(df: pd.DataFrame) -> float:
    """
    Calculates annualized volatility from daily returns.
    
    Why annualized?
    - So we can compare a 3-month dataset to a 1-year dataset.
    - Formula: daily_std * sqrt(252) where 252 = trading days per year.
    
    Interpretation:
    - 0.15 = 15% annual volatility (moderate, like S&P 500)
    - 0.40 = 40% annual volatility (high, like a growth stock)
    - 0.80 = 80% annual volatility (extreme, like crypto)
    """
    daily_returns = df["Close"].pct_change().dropna()
    daily_std = daily_returns.std()
    annualized_vol = daily_std * np.sqrt(252)
    
    return round(annualized_vol, 4)


def calculate_momentum(df: pd.DataFrame) -> dict:
    """
    Calculates price momentum over different time windows.
    
    Momentum = (current_price - price_N_days_ago) / price_N_days_ago
    
    Interpretation:
    - Positive = price is higher than N days ago (uptrend)
    - Negative = price is lower than N days ago (downtrend)
    """
    momentum = {}
    
    for days in [5, 10, 20, 30]:
        if len(df) >= days:
            past_price = df["Close"].iloc[-days]
            current_price = df["Close"].iloc[-1]
            mom = (current_price - past_price) / past_price
            momentum[f"{days}d"] = round(mom, 4)
        else:
            momentum[f"{days}d"] = None
    
    return momentum


def calculate_moving_averages(df: pd.DataFrame) -> dict:
    """
    Calculates simple moving averages (SMA).
    
    Interpretation:
    - Price above SMA = bullish signal
    - Price below SMA = bearish signal
    - Short MA above long MA = "golden cross" (bullish)
    """
    mas = {}
    
    for window in [10, 20, 50]:
        if len(df) >= window:
            mas[f"sma_{window}"] = round(df["Close"].rolling(window=window).mean().iloc[-1], 2)
        else:
            mas[f"sma_{window}"] = None
    
    return mas


def calculate_drawdown(df: pd.DataFrame) -> dict:
    """
    Calculates maximum drawdown.
    
    Drawdown at any point = (peak_so_far - current) / peak_so_far
    Max drawdown = worst drawdown in the entire period.
    
    Interpretation:
    - 0.10 = you lost 10% at worst (mild)
    - 0.30 = you lost 30% at worst (severe)
    - 0.50 = you lost 50% at worst (extreme)
    """
    # Cumulative maximum: the highest price seen so far
    rolling_max = df["Close"].cummax()
    
    # Drawdown at each point
    drawdown = (rolling_max - df["Close"]) / rolling_max
    
    max_drawdown = drawdown.max()
    
    # Find when the max drawdown occurred
    max_dd_idx = drawdown.idxmax()
    
    return {
        "max_drawdown": round(max_drawdown, 4),
        "peak_date": rolling_max.idxmax().strftime("%Y-%m-%d"),
        "trough_date": max_dd_idx.strftime("%Y-%m-%d"),
    }


def calculate_risk_score(volatility: float, max_drawdown: float) -> float:
    """
    Composite risk score combining volatility and drawdown.
    
    Scale: 0.0 (no risk) to 1.0 (extreme risk)
    
    This is a simple weighted average. In production, you'd use more factors.
    """
    # Normalize volatility: 0.80 = extreme, so divide by 0.80
    vol_score = min(volatility / 0.80, 1.0)
    
    # Drawdown is already 0-1
    dd_score = min(max_drawdown / 0.50, 1.0)  # 0.50 drawdown = max score
    
    # Weighted: 60% volatility, 40% drawdown
    risk_score = 0.6 * vol_score + 0.4 * dd_score
    
    return round(risk_score, 4)


def determine_trend(df: pd.DataFrame, mas: dict) -> str:
    """
    Determines price trend based on moving averages.
    
    Simple logic:
    - Price above SMA_20 = short-term uptrend
    - SMA_20 above SMA_50 = medium-term uptrend
    - Both = strong uptrend
    - Neither = downtrend
    """
    current_price = df["Close"].iloc[-1]
    
    sma_20 = mas.get("sma_20")
    sma_50 = mas.get("sma_50")
    
    if sma_20 and sma_50:
        if current_price > sma_20 and sma_20 > sma_50:
            return "strong_uptrend"
        elif current_price > sma_20:
            return "uptrend"
        elif current_price < sma_20 and sma_20 < sma_50:
            return "strong_downtrend"
        else:
            return "downtrend"
    elif sma_20:
        return "uptrend" if current_price > sma_20 else "downtrend"
    else:
        return "insufficient_data"


def analyze(ticker: str, df: pd.DataFrame) -> dict:
    """
    Main entry point for Quant Agent.
    
    Analyzes market data and returns structured metrics.
    
    Args:
        ticker: Stock symbol, e.g. "AAPL"
        df: pandas DataFrame with OHLCV data
    
    Returns:
        Dict with all metrics, confidence, and status.
    """
    # Validate input
    if df.empty or len(df) < 5:
        return {
            "agent": "quant",
            "ticker": ticker,
            "metrics": {},
            "confidence": 0.0,
            "status": "failed",
            "error": "Insufficient data (need at least 5 days)"
        }
    
    # Calculate all metrics
    returns = calculate_returns(df)
    volatility = calculate_volatility(df)
    momentum = calculate_momentum(df)
    mas = calculate_moving_averages(df)
    drawdown = calculate_drawdown(df)
    risk_score = calculate_risk_score(volatility, drawdown["max_drawdown"])
    trend = determine_trend(df, mas)
    
    # Determine confidence based on data quality
    confidence = 0.85 if len(df) >= 30 else 0.70 if len(df) >= 20 else 0.50
    
    # Build output
    result = {
        "agent": "quant",
        "ticker": ticker,
        "metrics": {
            "returns": returns,
            "volatility": volatility,
            "momentum": momentum,
            "moving_averages": mas,
            "drawdown": drawdown,
            "risk_score": risk_score,
            "trend": trend,
            "current_price": round(df["Close"].iloc[-1], 2),
            "data_points": len(df),
        },
        "confidence": confidence,
        "status": "complete",
    }
    
    return result