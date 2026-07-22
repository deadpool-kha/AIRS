"""
main.py

Entry point for AIRS.

Usage:
    python main.py --entity "AAPL"
    python main.py --entity "AAPL" --quant-only
    python main.py --entity "AAPL" --quant-only --show-sources
"""

import argparse
import pandas as pd

from data.db import init_db, save_market_data, get_market_data, save_entity, get_entity
from data.fetcher import fetch_with_retry
from agents.quant import analyze as quant_analyze


def run_quant_analysis(ticker: str, show_sources: bool = False):
    """
    Fetches data and runs Quant Agent.
    Demonstrates the full pipeline: fetch → save → analyze.
    """
    # Check if we have data in database
    rows = get_market_data(ticker, limit=100)
    
    if not rows:
        print(f"No data found for {ticker}. Fetching from Yahoo Finance...")
        df = fetch_with_retry(ticker, period="3mo")
        save_market_data(ticker, df)
    else:
        # Reconstruct DataFrame from database rows
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")
        
        # Rename columns to match yfinance format (capitalized)
        df = df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        })
        print(f"Using cached data: {len(df)} rows")
    
    # Run Quant Agent
    result = quant_analyze(ticker, df)
    
    # Pretty print results
    print(f"\n{'='*50}")
    print(f"QUANT ANALYSIS: {ticker}")
    print(f"{'='*50}")
    print(f"Trend: {result['metrics']['trend']}")
    print(f"Current Price: ${result['metrics']['current_price']}")
    print(f"Volatility (annual): {result['metrics']['volatility']:.2%}")
    print(f"Risk Score: {result['metrics']['risk_score']}")
    print(f"Max Drawdown: {result['metrics']['drawdown']['max_drawdown']:.2%}")
    print(f"Weekly Return: {result['metrics']['returns']['weekly']}%")
    print(f"Monthly Return: {result['metrics']['returns']['monthly']}%")
    print(f"Confidence: {result['confidence']}")
    if result.get('confidence_breakdown'):
        print(" Breakdown: ")
        for reason in result['confidence_breakdown']['reasons']:
            print(f' -{reason}')
    print(f"{'='*50}")
    
    # Source tracking display
    if show_sources and result['metrics'].get('_sources'):
        print("\n  Sources:")
        for metric, source in result['metrics']['_sources'].items():
            print(f"    {metric}: {source['source']} | {source['calculation']} | {source['calculated_at']}")
    elif result['metrics'].get('_sources'):
        print("\n  (Use --show-sources to display source tracking)")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="AIRS - Autonomous Investment Research System")
    parser.add_argument("--entity", type=str, required=True, help="Entity to analyze, e.g. 'AAPL'")
    parser.add_argument("--period", type=str, default="3mo", help="Data period: 1mo, 3mo, 6mo, 1y")
    parser.add_argument("--quant-only", action="store_true", help="Run only Quant Agent")
    parser.add_argument("--show-sources", action="store_true", help="Show source tracking for each metric")
    args = parser.parse_args()
    
    # Initialize database
    init_db()
    
    # Check if entity exists, create if not
    entity = get_entity(args.entity)
    if not entity:
        print(f"Creating new entity: {args.entity}")
        entity_id = save_entity(
            name=args.entity,
            ticker=args.entity,
            type_="stock"
        )
    else:
        entity_id = entity["id"]
        print(f"Found existing entity: {args.entity} (ID: {entity_id})")
    
    # Run analysis based on flags
    if args.quant_only:
        run_quant_analysis(args.entity, show_sources=args.show_sources)
    else:
        print("Full pipeline coming in later days. Use --quant-only for now.")
        print(f"To run Quant Agent: python main.py --entity {args.entity} --quant-only")
    
    return 0


if __name__ == "__main__":
    exit(main())