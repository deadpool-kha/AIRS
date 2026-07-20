"""
data/fetcher.py

Market data fetcher. Wraps yfinance to provide a clean interface.

Design decisions:
- yfinance is unofficial. It scrapes Yahoo Finance. It may break.
- We wrap it so if yfinance breaks, we only change this one file.
- We return raw pandas DataFrames. The caller decides what to do with them.
- No database logic here. This file only fetches. Saving is db.py's job.
"""

import yfinance as yf
import pandas as pd
import time


def fetch_stock_data(ticker: str, period: str = "3mo") -> pd.DataFrame:
    """
    Fetches historical stock data from Yahoo Finance.
    
    Args:
        ticker: Stock symbol, e.g. "AAPL" or "BTC-USD"
        period: How far back. Options: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
    
    Returns:
        pandas DataFrame with columns: Open, High, Low, Close, Volume
        Index is DatetimeIndex (dates)
    
    Raises:
        ValueError: If no data returned or ticker invalid
    
    Why we don't catch all exceptions:
    - Let the caller (main.py) decide what to do with failures.
    - If we swallow errors here, main.py can't show the user what went wrong.
    """
    print(f"Fetching {ticker} for period: {period}")
    
    # yfinance.Ticker creates an object that represents the stock
    stock = yf.Ticker(ticker)
    
    # .history() returns a DataFrame with OHLCV data
    # auto_adjust=True adjusts for splits and dividends
    df = stock.history(period=period, auto_adjust=True)
    
    # Defensive check: yfinance sometimes returns empty DataFrames silently
    if df.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'. Check if symbol is valid.")
    
    # yfinance sometimes returns MultiIndex columns (e.g., ('Close', 'AAPL')).
    # We flatten to simple column names.
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    
    # Verify we have the expected columns
    expected = {"Open", "High", "Low", "Close", "Volume"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}. Got: {list(df.columns)}")
    
    print(f"Fetched {len(df)} rows, from {df.index[0].date()} to {df.index[-1].date()}")
    
    return df


def fetch_with_retry(ticker: str, period: str = "3mo", max_retries: int = 3) -> pd.DataFrame:
    """
    Fetches data with exponential backoff retry.
    
    Why exponential backoff?
    - If Yahoo Finance is rate-limiting us, waiting longer each time helps.
    - 1s, 2s, 4s delays are polite and effective.
    """
    for attempt in range(max_retries):
        try:
            return fetch_stock_data(ticker, period)
        except Exception as e:
            if attempt == max_retries - 1:
                raise  # Last attempt failed, propagate the error
            
            wait = 2 ** attempt  # 1s, 2s, 4s
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)
    
    # Should never reach here, but just in case
    raise ValueError(f"Failed to fetch {ticker} after {max_retries} attempts")