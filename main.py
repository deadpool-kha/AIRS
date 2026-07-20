"""
main.py

Entry point for AIRS.

Usage:
    python main.py --entity "AAPL"
    
This script:
1. Initializes the database
2. Fetches market data for the entity
3. Saves it to the database
4. Reads it back to verify
"""

import argparse
from data.db import init_db, save_market_data, get_market_data, save_entity, get_entity
from data.fetcher import fetch_with_retry


def main():
    # argparse lets us run: python main.py --entity "AAPL"
    # Instead of hardcoding the ticker in the script
    parser = argparse.ArgumentParser(description="AIRS - Autonomous Investment Research System")
    parser.add_argument("--entity", type=str, required=True, help="Entity to analyze, e.g. 'AAPL'")
    parser.add_argument("--period", type=str, default="3mo", help="Data period: 1mo, 3mo, 6mo, 1y")
    args = parser.parse_args()
    
    # Step 1: Initialize database (creates tables if they don't exist)
    init_db()
    
    # Step 2: Check if entity exists, create if not
    entity = get_entity(args.entity)
    if not entity:
        print(f"Creating new entity: {args.entity}")
        entity_id = save_entity(
            name=args.entity,
            ticker=args.entity,
            type_="stock"  # Default, could be smarter later
        )
    else:
        entity_id = entity["id"]
        print(f"Found existing entity: {args.entity} (ID: {entity_id})")
    
    # Step 3: Fetch market data
    try:
        df = fetch_with_retry(args.entity, period=args.period)
    except ValueError as e:
        print(f"Error fetching data: {e}")
        return 1  # Exit with error code
    
    # Step 4: Save to database
    save_market_data(args.entity, df)
    
    # Step 5: Read back and display last 5 days
    rows = get_market_data(args.entity, limit=5)
    
    print(f"\nLast 5 days of {args.entity} data:")
    print("-" * 50)
    for row in rows:
        print(f"{row['date']}: Close=${row['close']:.2f}, Volume={row['volume']:,}")
    
    return 0  # Success


if __name__ == "__main__":
    exit(main())