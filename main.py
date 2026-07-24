"""
main.py

Entry point for AIRS.

Usage:
    python main.py --entity "AAPL"
    python main.py --entity "AAPL" --quant-only
    python main.py --entity "AAPL" --quant-only --show-sources
    python main.py --entity "AAPL" --repo bitcoin/bitcoin --hypotheses
"""

import argparse
import pandas as pd

from agents.risk import RiskAgent
from data.db import init_db, save_market_data, get_market_data, save_entity, get_entity
from data.fetcher import fetch_with_retry
from agents.quant import analyze as quant_analyze
from agents.technical import analyze as technical_analyze
from reports.hypothesis import generate_hypotheses, format_hypotheses
from agents.business import BusinessAgent


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


def run_technical_analysis(repo: str):
    """
    Runs Technical Agent on a GitHub repo.
    """
    print(f"\nFetching GitHub data for {repo}...")
    
    result = technical_analyze(repo)
    
    if result["status"] == "failed":
        print(f"Technical analysis failed: {result.get('error', 'Unknown error')}")
        return result
    
    print(f"\n{'='*50}")
    print(f"TECHNICAL ANALYSIS: {repo}")
    print(f"{'='*50}")
    print(f"Total Commits: {result['metrics']['total_commits']}")
    print(f"Commit Frequency: {result['metrics']['commit_frequency']}/week")
    print(f"Contributors: {result['metrics']['contributor_count']}")
    print(f"Open Issues: {result['metrics']['open_issues']}")
    print(f"Days Since Commit: {result['metrics']['days_since_commit']}")
    print(f"Health Score: {result['metrics']['health_score']}")
    print(f"Confidence: {result['confidence']}")
    print(f"{'='*50}")
    
    return result

def run_business_analysis(entity: str, ticker: str = None):
    """
    Runs Business Agent for news analysis.
    """
    print(f"\nFetching business news for {entity}...")
    
    business_agent = BusinessAgent()
    
    try:
        result = business_agent.analyze(entity=entity, ticker=ticker)
        
        print(f"\n{'='*50}")
        print(f"BUSINESS ANALYSIS: {entity}")
        print(f"{'='*50}")
        print(f"Summary: {result['summary'][:200]}...")
        print(f"Signals: {result['metrics']['signal_count']} found")
        print(f"  Positive: {result['metrics']['positive_signals']}")
        print(f"  Negative: {result['metrics']['negative_signals']}")
        print(f"Catalysts: {result['metrics']['catalyst_count']}")
        print(f"Risks: {result['metrics']['risk_count']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Status: {result['status']}")
        print(f"{'='*50}")
        
        if result['status'] == 'complete':
            print("\n  Top Signals:")
            for s in result['signals'][:5]:
                print(f"    [{s['type'].upper()}] {s['category']}: {s['description']}")
            
            if result['catalysts']:
                print("\n  Catalysts:")
                for c in result['catalysts'][:3]:
                    print(f"    → {c}")
            
            if result['risks']:
                print("\n  Risks:")
                for r in result['risks'][:3]:
                    print(f"    ⚠ {r}")
        
        return result
        
    except ConnectionError as e:
        print(f"⚠️  Business Agent skipped: {e}")
        print("     (Start Ollama with: ollama serve)")
        return {
            "agent": "business",
            "entity": entity,
            "status": "failed",
            "error": str(e),
            "confidence": 0.0,
        }
    except Exception as e:
        print(f"⚠️  Business Agent error: {e}")
        return {
            "agent": "business",
            "entity": entity,
            "status": "failed",
            "error": str(e),
            "confidence": 0.0,
        }


def run_risk_analysis(entity: str, agent_outputs: dict):
    """
    Runs Risk Agent on combined agent outputs.
    """
    print(f"\nAnalyzing risks for {entity}...")
    
    risk_agent = RiskAgent()
    result = risk_agent.analyze(entity=entity, agent_outputs=agent_outputs)
    
    print(f"\n{'='*50}")
    print(f"RISK ANALYSIS: {entity}")
    print(f"{'='*50}")
    print(f"Overall Risk: {result['metrics']['overall_risk'].upper()}")
    print(f"Risks Found: {result['metrics']['risk_count']}")
    print(f"Warnings: {result['metrics']['warning_count']}")
    print(f"High Severity: {result['metrics']['high_severity_count']}")
    print(f"Confidence: {result['confidence']}")
    print(f"{'='*50}")
    
    if result['risks']:
        print("\n  🚨 RISKS:")
        for r in result['risks']:
            icon = "🔴" if r['severity'] == 'high' else "🟡"
            print(f"    {icon} [{r['category'].upper()}] {r['description']}")
            print(f"       Source: {r['source']}")
    
    if result['warnings']:
        print("\n  ⚠️  WARNINGS:")
        for w in result['warnings']:
            print(f"    🟡 [{w['category'].upper()}] {w['description']}")
            print(f"       Source: {w['source']}")
    
    return result

def main():
    
    parser = argparse.ArgumentParser(description="AIRS - Autonomous Investment Research System")
    parser.add_argument("--entity", type=str, help="Entity to analyze, e.g. 'AAPL'")
    parser.add_argument("--repo", type=str, help="GitHub repo to analyze, e.g. 'bitcoin/bitcoin'")
    parser.add_argument("--period", type=str, default="3mo", help="Data period: 1mo, 3mo, 6mo, 1y")
    parser.add_argument("--quant-only", action="store_true", help="Run only Quant Agent")
    parser.add_argument("--technical-only", action="store_true", help="Run only Technical Agent")
    parser.add_argument("--show-sources", action="store_true", help="Show source tracking for each metric")
    parser.add_argument("--hypotheses", action="store_true", help="Generate bull/bear/base hypotheses from agent outputs")
    parser.add_argument("--business-only", action="store_true", help="Run only Business Agent")
    parser.add_argument("--ticker", type=str, help="Stock/crypto ticker for better news matching")
    parser.add_argument("--risk-only", action="store_true", help="Run only Risk Agent (requires other agent outputs)")
    args = parser.parse_args()
    
    # Validate: need entity for quant, need repo for technical
    if not args.technical_only and not args.entity:
        parser.error("--entity is required unless using --technical-only")
    
    if args.technical_only and not args.repo:
        parser.error("--repo is required when using --technical-only")
    
    # Hypotheses mode requires both entity and repo
    if args.hypotheses and (not args.entity or not args.repo):
        parser.error("--hypotheses requires both --entity and --repo")
    
    # Risk-only needs other agents first
    if args.risk_only:
        parser.error("--risk-only requires running other agents first. Use --hypotheses instead.")
    
    # Initialize database
    init_db()
    
    # Run based on flags
    if args.technical_only:
        run_technical_analysis(args.repo)
    elif args.quant_only:
        run_quant_analysis(args.entity, show_sources=args.show_sources)
    elif args.business_only:
        if not args.entity:
            parser.error("--entity is required when using --business-only")
        run_business_analysis(args.entity, ticker=args.ticker)
    elif args.hypotheses:
        # Run all agents and generate hypotheses
        quant_result = run_quant_analysis(args.entity, show_sources=args.show_sources)
        technical_result = run_technical_analysis(args.repo)
        business_result = run_business_analysis(args.entity, ticker=args.ticker)
        
        # Build agent outputs for risk analysis
        full_outputs = {
            "quant": quant_result,
            "technical": technical_result,
            "business": business_result,
        }
        
        # Run Risk Agent
        risk_result = run_risk_analysis(args.entity, full_outputs)
        
        # Build agent outputs dict for hypothesis engine
        agent_outputs = {
            "quant": quant_result,
            "technical": technical_result,
            "business": business_result,
            "risk": risk_result,
        }
        
        # Generate and display hypotheses
        hypotheses = generate_hypotheses(args.entity, agent_outputs)
        print(format_hypotheses(hypotheses))
        
    elif args.repo:
        # Run both (without hypotheses)
        run_quant_analysis(args.entity, show_sources=args.show_sources)
        run_technical_analysis(args.repo)
    else:
        run_quant_analysis(args.entity, show_sources=args.show_sources)
    
    return 0


if __name__ == "__main__":
    exit(main())