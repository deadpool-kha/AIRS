"""
agents/quant.py
Issue #9b: Evidence-Driven Loop Evolution

Quant Agent: Numerical analysis of market data.

Changes for Issue #9b:
- Added tiered computation with DATA DEPTH evolution:
  Tier 1: 3mo (≈60 trading days) → basic features
  Tier 2: 6mo (≈120 trading days) → basic + extended features
  Tier 3: 1y (≈250 trading days) → basic + extended + full features
- On deeper tiers, lower-tier features are RECOMPUTED with more data
  (the Register always holds the best available version)
- Added new features: RSI, MACD, volume_profile, ATR, beta, correlation_matrix,
  volatility_regime
- EvidenceRegister integration: checks existing evidence before computing,
  skips if existing data is deeper or equal
- Preserved all existing functions for backward compatibility

Design:
- Pure functions (calculate_*) remain stateless
- QuantAgent class handles data lifecycle + tier gating
- DataFrame cached as "price_data" in register to avoid re-fetching
- Each feature stores its data_points provenance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from core.evidence import EvidenceRegister
from data.db import get_market_data, save_market_data
from data.fetcher import fetch_with_retry


# ═══════════════════════════════════════════════════════════════════════════════
# EXISTING FUNCTIONS (unchanged behavior, preserved for backward compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_returns(df: pd.DataFrame) -> dict:
    """Calculates daily, weekly, and monthly returns."""
    daily_returns = df["Close"].pct_change().dropna()
    weekly_return = (df["Close"].iloc[-1] / df["Close"].iloc[-5] - 1) if len(df) >= 5 else None
    monthly_return = (df["Close"].iloc[-1] / df["Close"].iloc[-21] - 1) if len(df) >= 21 else None

    return {
        "daily_mean": round(daily_returns.mean() * 100, 4),
        "daily_std": round(daily_returns.std() * 100, 4),
        "weekly": round(weekly_return * 100, 2) if weekly_return is not None else None,
        "monthly": round(monthly_return * 100, 2) if monthly_return is not None else None,
    }


def calculate_volatility(df: pd.DataFrame) -> float:
    """Annualized volatility from daily returns."""
    daily_returns = df["Close"].pct_change().dropna()
    daily_std = daily_returns.std()
    annualized_vol = daily_std * np.sqrt(252)
    return round(annualized_vol, 4)


def calculate_momentum(df: pd.DataFrame) -> dict:
    """Price momentum over 5d, 10d, 20d, 30d windows."""
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
    """Simple moving averages (10, 20, 50 day)."""
    mas = {}
    for window in [10, 20, 50]:
        if len(df) >= window:
            mas[f"sma_{window}"] = round(df["Close"].rolling(window=window).mean().iloc[-1], 2)
        else:
            mas[f"sma_{window}"] = None
    return mas


def calculate_drawdown(df: pd.DataFrame) -> dict:
    """Maximum drawdown with peak/trough dates."""
    rolling_max = df["Close"].cummax()
    drawdown = (rolling_max - df["Close"]) / rolling_max
    max_drawdown = drawdown.max()
    max_dd_idx = drawdown.idxmax()

    return {
        "max_drawdown": round(max_drawdown, 4),
        "peak_date": rolling_max.idxmax().strftime("%Y-%m-%d"),
        "trough_date": max_dd_idx.strftime("%Y-%m-%d"),
    }


def calculate_risk_score(volatility: float, max_drawdown: float) -> float:
    """Composite risk score (0.0 = no risk, 1.0 = extreme)."""
    vol_score = min(volatility / 0.80, 1.0)
    dd_score = min(max_drawdown / 0.50, 1.0)
    risk_score = 0.6 * vol_score + 0.4 * dd_score
    return round(risk_score, 4)


def determine_trend(df: pd.DataFrame, mas: dict) -> str:
    """Price trend based on moving averages."""
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
    return "insufficient_data"


def calculate_confidence(df, metrics):
    """Confidence score based on data quality and metric completeness."""
    reasons = []
    score = 0.0

    if len(df) >= 30:
        score += 0.30
        reasons.append("Sufficient data: 30+ days")
    elif len(df) >= 20:
        score += 0.20
        reasons.append("Limited data: 20-29 days")
    else:
        reasons.append("Insufficient data: <20 days")

    required = ["volatility", "momentum", "drawdown", "trend"]
    present = sum(1 for m in required if metrics.get(m) is not None)
    metric_score = present / len(required)
    score += 0.30 * metric_score
    reasons.append(f"Metrics complete: {present}/{len(required)}")

    latest = df.index[-1]
    now = pd.Timestamp.now().tz_localize(None)
    latest = latest.tz_localize(None) if hasattr(latest, 'tz') and latest.tz is not None else latest
    days_old = (now - latest).days
    if days_old <= 1:
        score += 0.20
        reasons.append("Data fresh: <=1 day old")
    elif days_old <= 3:
        score += 0.10
        reasons.append("Data stale: 2-3 days old")
    else:
        reasons.append(f"Data old: {days_old} days")

    score += 0.20
    reasons.append("Deterministic calculations: reproducible")

    return {
        "score": round(score, 4),
        "reasons": reasons,
        "components": {
            "data_sufficiency": 0.30 if len(df) >= 30 else 0.20 if len(df) >= 20 else 0.0,
            "metric_completeness": round(metric_score, 4),
            "data_freshness": 0.20 if days_old <= 1 else 0.10 if days_old <= 3 else 0.0,
            "calculation_stability": 0.20
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NEW FUNCTIONS (Issue #9b — Extended & Full tier features)
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_rsi(df: pd.DataFrame, window: int = 14) -> Optional[float]:
    """Relative Strength Index. >70 overbought, <30 oversold."""
    if len(df) < window + 1:
        return None
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta.where(delta < 0, 0.0))
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[dict]:
    """MACD with signal line and histogram."""
    if len(df) < slow + signal:
        return None
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    hist_val = histogram.iloc[-1]
    hist_prev = histogram.iloc[-2] if len(histogram) > 1 else 0

    if hist_val > 0 and hist_prev <= 0:
        signal_str = "bullish_crossover"
    elif hist_val < 0 and hist_prev >= 0:
        signal_str = "bearish_crossover"
    elif hist_val > 0:
        signal_str = "bullish"
    else:
        signal_str = "bearish"

    return {
        "macd_line": round(macd_line.iloc[-1], 4),
        "signal_line": round(signal_line.iloc[-1], 4),
        "histogram": round(hist_val, 4),
        "signal": signal_str,
    }


def calculate_volume_profile(df: pd.DataFrame) -> Optional[dict]:
    """Volume analysis: average, trend, relative volume."""
    if "Volume" not in df.columns or df["Volume"].isna().all():
        return None
    avg_volume = df["Volume"].mean()
    recent_avg = df["Volume"].iloc[-5:].mean()
    volume_trend = "increasing" if recent_avg > avg_volume * 1.1 else \
                   "decreasing" if recent_avg < avg_volume * 0.9 else "stable"

    return {
        "avg_volume": int(avg_volume),
        "volume_trend": volume_trend,
        "relative_volume": round(df["Volume"].iloc[-1] / avg_volume, 2) if avg_volume > 0 else 0.0,
    }


def calculate_atr(df: pd.DataFrame, window: int = 14) -> Optional[float]:
    """Average True Range — volatility using high/low/close."""
    if len(df) < window + 1 or not all(c in df.columns for c in ["High", "Low", "Close"]):
        return None
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    return round(atr.iloc[-1], 4)


def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series) -> Optional[float]:
    """Market beta: covariance(stock, market) / variance(market)."""
    aligned = pd.concat([stock_returns, market_returns], axis=1).dropna()
    if len(aligned) < 30:
        return None
    try:
        covariance = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])[0][1]
        market_variance = np.var(aligned.iloc[:, 1])
        if market_variance == 0:
            return None
        return round(covariance / market_variance, 4)
    except Exception:
        return None


def calculate_correlation_matrix(df: pd.DataFrame, benchmark_dfs: Optional[Dict[str, pd.DataFrame]] = None) -> Optional[dict]:
    """Correlation between stock and benchmark assets."""
    if len(df) < 30:
        return None
    stock_returns = df["Close"].pct_change().dropna()
    correlations = {}
    if benchmark_dfs:
        for ticker, bench_df in benchmark_dfs.items():
            if len(bench_df) < 30:
                continue
            bench_returns = bench_df["Close"].pct_change().dropna()
            aligned = pd.concat([stock_returns, bench_returns], axis=1).dropna()
            if len(aligned) >= 20:
                corr = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
                correlations[ticker] = round(corr, 4)
    return correlations if correlations else None


def classify_volatility_regime(atr: float, current_price: float) -> str:
    """Classify volatility regime based on ATR as % of price."""
    if current_price <= 0:
        return "unknown"
    atr_pct = atr / current_price
    if atr_pct < 0.01:
        return "low"
    elif atr_pct < 0.025:
        return "normal"
    elif atr_pct < 0.05:
        return "elevated"
    else:
        return "extreme"


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def analyze(ticker: str, df: pd.DataFrame) -> dict:
    """
    Main entry point for Quant Agent (backward-compatible).
    Computes ALL metrics in a single call. Preserved for direct use.
    """
    if df.empty or len(df) < 5:
        return {
            "agent": "quant",
            "ticker": ticker,
            "metrics": {},
            "confidence": 0.0,
            "status": "failed",
            "error": "Insufficient data (need at least 5 days)"
        }

    returns = calculate_returns(df)
    volatility = calculate_volatility(df)
    momentum = calculate_momentum(df)
    mas = calculate_moving_averages(df)
    drawdown = calculate_drawdown(df)
    risk_score = calculate_risk_score(volatility, drawdown["max_drawdown"])
    trend = determine_trend(df, mas)
    rsi = calculate_rsi(df)
    macd = calculate_macd(df)
    volume_profile = calculate_volume_profile(df)
    atr = calculate_atr(df)
    volatility_regime = classify_volatility_regime(atr, df["Close"].iloc[-1]) if atr else "unknown"

    now = datetime.now(timezone.utc).isoformat()
    period = f"{len(df)}d"

    metrics = {
        "returns": returns,
        "volatility": volatility,
        "momentum": momentum,
        "moving_averages": mas,
        "drawdown": drawdown,
        "risk_score": risk_score,
        "trend": trend,
        "current_price": round(df["Close"].iloc[-1], 2),
        "data_points": len(df),
        "rsi": rsi,
        "macd": macd,
        "volume_profile": volume_profile,
        "atr": atr,
        "volatility_regime": volatility_regime,
    }

    metrics["_sources"] = {
        k: {"source": "yfinance", "ticker": ticker, "period": period, "calculated_at": now}
        for k in metrics.keys() if not k.startswith("_")
    }

    confidence = calculate_confidence(df, metrics)

    return {
        "agent": "quant",
        "ticker": ticker,
        "metrics": metrics,
        "confidence": confidence["score"],
        "confidence_breakdown": confidence,
        "status": "complete",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# QUANT AGENT CLASS (Issue #9b — Evidence-Driven Tiered Computation)
# ═══════════════════════════════════════════════════════════════════════════════

class QuantAgent:
    """
    Tiered Quant Agent for evidence-driven loop architecture.

    Data depth evolution:
        Tier 1: period="3mo" (~60 trading days) → basic features
        Tier 2: period="6mo" (~120 trading days) → basic + extended
        Tier 3: period="1y" (~250 trading days) → basic + extended + full

    On deeper tiers, lower-tier features are RECOMPUTED with more data.
    The Evidence Register always holds the best available version.

    Usage:
        agent = QuantAgent()
        outputs = agent.run("AAPL", tier=1, evidence_register=register)
        # Returns dict of features computed with 3mo data
        # Loop controller writes these to register with provenance
    """

    DEFAULT_TIER_PERIODS = {
        1: "3mo",
        2: "6mo",
        3: "1y",
    }

    # Features computed at each tier (cumulative — tier N computes tiers 1..N)
    TIER_FEATURES = {
        1: ["returns", "volatility", "momentum", "moving_averages", 
            "drawdown", "risk_score", "trend", "current_price", "data_points"],
        2: ["rsi", "macd", "volume_profile"],
        3: ["atr", "volatility_regime", "beta", "correlation_matrix"],
    }

    BENCHMARK_TICKERS = ["SPY", "QQQ"]

    def __init__(self, tier_periods: Optional[Dict[int, str]] = None):
        self.tier_periods = tier_periods or self.DEFAULT_TIER_PERIODS.copy()
        self._benchmark_cache: Dict[str, pd.DataFrame] = {}

    def run(self, ticker: str, tier: int, evidence_register: EvidenceRegister, **kwargs) -> Dict[str, Any]:
        """
        Compute quant features for the given tier with appropriate data depth.

        Args:
            ticker: Stock symbol
            tier: 1 (3mo), 2 (6mo), or 3 (1y)
            evidence_register: Shared evidence register (read to check existing depth)

        Returns:
            Dict of {feature_name: computed_value} for features that were
            either NEW or UPGRADED with deeper data.
        """
        period = self.tier_periods.get(tier, "3mo")
        outputs = {}

        # Fetch data for this tier's period
        df = self._fetch_or_load_data(ticker, period)
        if df is None or df.empty:
            return {"_error": f"No data available for {ticker} (period={period})", "_tier": tier}

        data_points = len(df)
        outputs["price_data"] = df  # Always return for register caching

        # Determine which features to compute for this tier
        features_this_tier = []
        for t in range(1, tier + 1):
            features_this_tier.extend(self.TIER_FEATURES[t])

        # Compute each feature, skipping only if existing version has equal or deeper data
        for feature in features_this_tier:
            if evidence_register.has(feature):
                meta = evidence_register.get_meta(feature)
                # Skip if existing was computed with equal or more data points
                if meta.data_points is not None and meta.data_points >= data_points:
                    continue

            try:
                value = self._compute_feature(ticker, feature, df, evidence_register)
                if value is not None:
                    outputs[feature] = value
            except Exception as e:
                outputs[f"_{feature}_error"] = str(e)

        return outputs

    def _fetch_or_load_data(self, ticker: str, period: str) -> Optional[pd.DataFrame]:
        """Fetch market data from DB cache or Yahoo Finance."""
        # Try DB cache first (unlimited rows for deeper history)
        rows = get_market_data(ticker, limit=500)

        if rows:
            df = pd.DataFrame(rows)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").set_index("date")
            df = df.rename(columns={
                "open": "Open", "high": "High", "low": "Low",
                "close": "Close", "volume": "Volume"
            })
            # If cached data is deep enough, use it
            if len(df) >= self._min_rows_for_period(period):
                return df

        # Fetch from Yahoo Finance
        try:
            df = fetch_with_retry(ticker, period=period)
            save_market_data(ticker, df)
            return df
        except Exception:
            return None

    def _min_rows_for_period(self, period: str) -> int:
        """Minimum rows needed to satisfy a period request."""
        mapping = {"1mo": 20, "3mo": 50, "6mo": 100, "1y": 200, "2y": 400}
        return mapping.get(period, 50)

    def _compute_feature(self, ticker: str, feature: str, df: pd.DataFrame, 
                         register: EvidenceRegister) -> Any:
        """Route to the appropriate calculation function."""

        # ── Tier 1: Basic ─────────────────────────────────────────────────────
        if feature == "returns":
            return calculate_returns(df)

        if feature == "volatility":
            return calculate_volatility(df)

        if feature == "momentum":
            return calculate_momentum(df)

        if feature == "moving_averages":
            return calculate_moving_averages(df)

        if feature == "drawdown":
            return calculate_drawdown(df)

        if feature == "risk_score":
            vol = register.get("volatility") if register.has("volatility") else calculate_volatility(df)
            dd_data = register.get("drawdown") if register.has("drawdown") else calculate_drawdown(df)
            dd = dd_data["max_drawdown"] if isinstance(dd_data, dict) else dd_data
            return calculate_risk_score(vol, dd)

        if feature == "trend":
            mas = register.get("moving_averages") if register.has("moving_averages") else calculate_moving_averages(df)
            return determine_trend(df, mas)

        if feature == "current_price":
            return round(df["Close"].iloc[-1], 2)

        if feature == "data_points":
            return len(df)

        # ── Tier 2: Extended ──────────────────────────────────────────────────
        if feature == "rsi":
            return calculate_rsi(df)

        if feature == "macd":
            return calculate_macd(df)

        if feature == "volume_profile":
            return calculate_volume_profile(df)

        # ── Tier 3: Full ──────────────────────────────────────────────────────
        if feature == "atr":
            return calculate_atr(df)

        if feature == "volatility_regime":
            atr = register.get("atr") if register.has("atr") else calculate_atr(df)
            price = df["Close"].iloc[-1]
            if atr is not None:
                return classify_volatility_regime(atr, price)
            return "unknown"

        if feature == "beta":
            return self._compute_beta(ticker, df)

        if feature == "correlation_matrix":
            return self._compute_correlation_matrix(ticker, df)

        return None

    def _compute_beta(self, ticker: str, df: pd.DataFrame) -> Optional[float]:
        """Compute market beta using SPY as benchmark."""
        stock_returns = df["Close"].pct_change().dropna()
        spy_df = self._get_benchmark_data("SPY")
        if spy_df is None or len(spy_df) < 30:
            return None
        market_returns = spy_df["Close"].pct_change().dropna()
        return calculate_beta(stock_returns, market_returns)

    def _compute_correlation_matrix(self, ticker: str, df: pd.DataFrame) -> Optional[dict]:
        """Compute correlation with benchmark indices."""
        benchmark_dfs = {}
        for bench in self.BENCHMARK_TICKERS:
            bench_df = self._get_benchmark_data(bench)
            if bench_df is not None:
                benchmark_dfs[bench] = bench_df
        return calculate_correlation_matrix(df, benchmark_dfs)

    def _get_benchmark_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """Fetch benchmark data with caching across tiers."""
        if ticker in self._benchmark_cache:
            return self._benchmark_cache[ticker]

        rows = get_market_data(ticker, limit=500)
        if rows:
            df = pd.DataFrame(rows)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").set_index("date")
            df = df.rename(columns={
                "open": "Open", "high": "High", "low": "Low",
                "close": "Close", "volume": "Volume"
            })
            self._benchmark_cache[ticker] = df
            return df

        try:
            df = fetch_with_retry(ticker, period="1y")
            save_market_data(ticker, df)
            self._benchmark_cache[ticker] = df
            return df
        except Exception:
            return None