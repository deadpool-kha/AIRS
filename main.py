"""
main.py
Issue #9b+: Evidence-Driven Loop Evolution

Entry point for AIRS.
"""

import argparse
import pandas as pd

from agents.critic import CriticAgent
from controller.loop import EvidenceDrivenLoop
from agents.risk import RiskAgent
from data.db import init_db, save_market_data, get_market_data, save_entity, get_entity
from data.fetcher import fetch_with_retry
from agents.quant import analyze as quant_analyze, QuantAgent
from agents.technical import analyze as technical_analyze
from reports.hypothesis import generate_hypotheses, generate_from_register, format_hypotheses
from agents.business import BusinessAgent


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT RUNNER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def run_quant_analysis(ticker: str, show_sources: bool = False, period: str = "3mo", refresh: bool = False):
    """Fetches data and runs Quant Agent (backward-compatible single-shot)."""
    rows = get_market_data(ticker, limit=100)

    if not rows or refresh:
        print(f"{'Refreshing' if refresh else 'No data found for'} {ticker}. Fetching from Yahoo Finance (period={period})...")
        try:
            df = fetch_with_retry(ticker, period=period)
            save_market_data(ticker, df)
        except Exception as e:
            print(f"⚠️  Quant Agent failed: {e}")
            return {
                "agent": "quant", "entity": ticker, "status": "failed",
                "error": str(e), "confidence": 0.0, "metrics": {},
            }
    else:
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")
        df = df.rename(columns={
            "open": "Open", "high": "High", "low": "Low",
            "close": "Close", "volume": "Volume"
        })
        print(f"Using cached data: {len(df)} rows")

    result = quant_analyze(ticker, df)

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
    print(f"RSI: {result['metrics'].get('rsi', 'N/A')}")
    macd = result['metrics'].get('macd', {})
    if macd:
        print(f"MACD Signal: {macd.get('signal', 'N/A')}")
    print(f"Confidence: {result['confidence']}")
    if result.get('confidence_breakdown'):
        print(" Breakdown: ")
        for reason in result['confidence_breakdown']['reasons']:
            print(f' -{reason}')
    print(f"{'='*50}")

    if show_sources and result['metrics'].get('_sources'):
        print("\n  Sources:")
        for metric, source in result['metrics']['_sources'].items():
            if metric.startswith("_"): continue
            print(f"    {metric}: {source['source']} | {source['calculation']} | {source['calculated_at']}")
    elif result['metrics'].get('_sources'):
        print("\n  (Use --show-sources to display source tracking)")

    return result


def run_technical_analysis(repo: str):
    """Runs Technical Agent on a GitHub repo."""
    print(f"\nFetching GitHub data for {repo}...")
    result = technical_analyze(repo)

    if result["status"] == "failed":
        print(f"Technical analysis failed: {result.get('error', 'Unknown error')}")
        print("     (This is normal for private repos or non-GitHub companies)")
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


def run_business_analysis(entity: str, ticker: str = None, broad_search: bool = False):
    """Runs Business Agent for news analysis."""
    print(f"\nFetching business news for {entity}...")
    business_agent = BusinessAgent()
    actual_ticker = None if broad_search else ticker

    try:
        result = business_agent.analyze(entity=entity, ticker=actual_ticker)

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
        return {"agent": "business", "entity": entity, "status": "failed",
                "error": str(e), "confidence": 0.0}
    except Exception as e:
        print(f"⚠️  Business Agent error: {e}")
        return {"agent": "business", "entity": entity, "status": "failed",
                "error": str(e), "confidence": 0.0}


def run_risk_analysis(entity: str, agent_outputs: dict):
    """Runs Risk Agent on combined agent outputs."""
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

    if result.get('risks'):
        print("\n  🚨 RISKS:")
        for r in result['risks']:
            icon = "🔴" if r['severity'] == 'high' else "🟡"
            print(f"    {icon} [{r['category'].upper()}] {r['description']}")
            print(f"       Source: {r['source']}")

    if result.get('warnings'):
        print("\n  ⚠️  WARNINGS:")
        for w in result['warnings']:
            print(f"    🟡 [{w['category'].upper()}] {w['description']}")
            print(f"       Source: {w['source']}")

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="AIRS - Autonomous Investment Research System (Issue #9b+)")
    parser.add_argument("--entity", type=str, help="Entity to analyze, e.g. 'AAPL' or 'Bitcoin'")
    parser.add_argument("--repo", type=str, help="GitHub repo, e.g. 'bitcoin/bitcoin'")
    parser.add_argument("--period", type=str, default="3mo", help="Data period (single-shot only): 1mo, 3mo, 6mo, 1y")
    parser.add_argument("--quant-only", action="store_true", help="Run only Quant Agent (single-shot)")
    parser.add_argument("--technical-only", action="store_true", help="Run only Technical Agent")
    parser.add_argument("--show-sources", action="store_true", help="Show source tracking")
    parser.add_argument("--hypotheses", action="store_true", help="Run full evidence-driven loop with hypotheses")
    parser.add_argument("--business-only", action="store_true", help="Run only Business Agent")
    parser.add_argument("--ticker", type=str, help="Stock/crypto ticker for quant + better news matching")
    parser.add_argument("--risk-only", action="store_true", help="Run only Risk Agent (legacy, not recommended)")
    parser.add_argument("--critic", action="store_true", help="Run Critic evaluation (legacy mode)")
    args = parser.parse_args()

    # Validate inputs
    if not args.technical_only and not args.entity:
        parser.error("--entity is required unless using --technical-only")

    if args.technical_only and not args.repo:
        parser.error("--repo is required when using --technical-only")

    if args.risk_only:
        parser.error("--risk-only is not supported. Use --hypotheses for full analysis.")

    # Initialize database
    init_db()

    # ═══════════════════════════════════════════════════════════════════════════
    # SINGLE-SHOT MODES (backward-compatible CLI usage)
    # ═══════════════════════════════════════════════════════════════════════════

    if args.technical_only:
        run_technical_analysis(args.repo)
        return 0

    if args.quant_only:
        run_quant_analysis(args.entity, show_sources=args.show_sources, period=args.period)
        return 0

    if args.business_only:
        if not args.entity:
            parser.error("--entity is required when using --business-only")
        run_business_analysis(args.entity, ticker=args.ticker)
        return 0

    # ═══════════════════════════════════════════════════════════════════════════
    # EVIDENCE-DRIVEN LOOP MODE (Issue #9b+ — default when --hypotheses)
    # ═══════════════════════════════════════════════════════════════════════════

    if args.hypotheses:
        print(f"\n{'#'*60}")
        print("# AIRS Evidence-Driven Loop (Issue #9b+)")
        print(f"{'#'*60}")

        # Create agent instances
        quant_agent = QuantAgent()
        critic_agent = CriticAgent()
        risk_agent = RiskAgent()

        # Create the evidence-driven loop
        loop = EvidenceDrivenLoop(
            business_runner=lambda: run_business_analysis(args.entity, ticker=args.ticker),
            technical_runner=(lambda: run_technical_analysis(args.repo)) if args.repo else None,
            quant_agent=quant_agent,
            critic_agent=critic_agent,
            risk_agent=risk_agent,
            hypotheses_runner=generate_from_register,
        )

        # Run the loop
        results = loop.run(
            entity=args.entity,
            ticker=args.ticker or args.entity,
            repo=args.repo,
            config={
                'hypotheses': True,
                'show_sources': args.show_sources,
            }
        )

        # ═══════════════════════════════════════════════════════════════════════
        # FINAL RESULTS SUMMARY — DASHBOARD STYLE
        # ═══════════════════════════════════════════════════════════════════════

        print(f"\n{'='*60}")
        print("FINAL RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Entity: {results['entity']}")
        print(f"Asset Type: {results['asset_type']}")
        print(f"Iterations: {results['iterations']}")
        print(f"Halt reason: {results['halt_reason']}")
        print(f"Evidence collected: {results['evidence_count']} items")

        # ── Dashboard ──
        dash = results.get('dashboard', {})
        if dash:
            print(f"\n{'─'*50}")
            print("AUDIT DASHBOARD")
            print(f"{'─'*50}")
            dq = dash.get('data_quality', {})
            cov = dash.get('coverage', {})
            agr = dash.get('agreement', {})
            stab = dash.get('stability', {})
            print(f"  Data Quality:  {dq.get('score', 0):.0%}")
            print(f"  Coverage:      {cov.get('score', 0):.0%} ({cov.get('present', 0)}/{cov.get('required', 0)} features)")
            print(f"  Agreement:     {agr.get('level', '?')} — {agr.get('details', '')}")
            print(f"  Stability:     {stab.get('level', '?')} — {stab.get('details', '')}")

        # ── Directional Bias & Uncertainty ──
        hyp = results.get('hypotheses', {})
        if hyp:
            bias = hyp.get('directional_bias', {})
            uncertainty = hyp.get('uncertainty', {})
            if bias:
                print(f"\n{'─'*50}")
                print("INVESTMENT THESIS")
                print(f"{'─'*50}")
                print(f"  Directional Bias: {bias.get('net', 'unknown').upper()}")
                print(f"    Bullish strength: {bias.get('bull_strength', 0):.2f} ({bias.get('bull_evidence_count', 0)} claims)")
                print(f"    Bearish strength: {bias.get('bear_strength', 0):.2f} ({bias.get('bear_evidence_count', 0)} claims)")
                print(f"    Net score: {bias.get('directional_score', 0):+.2f}")
            if uncertainty:
                print(f"\n  Uncertainty: {uncertainty.get('level', 'Unknown')} ({uncertainty.get('score', 0):.0%})")
                print(f"    {uncertainty.get('reason', '')}")

        # ── Active Questions ──
        questions = results.get('active_questions', [])
        if questions:
            print(f"\n{'─'*50}")
            print(f"ACTIVE QUESTIONS ({len(questions)})")
            print(f"{'─'*50}")
            for q in questions:
                print(f"  ? {q['question']}")
                print(f"    Why it matters: {q['why_it_matters']}")
                if q.get('can_deeper_data_answer'):
                    print(f"    → Deeper data may resolve this")
                else:
                    print(f"    → Requires human judgment; data cannot answer")

        # ── Unresolved Contradictions ──
        unresolved = results.get('unresolved_contradictions', [])
        if unresolved:
            print(f"\n{'─'*50}")
            print(f"UNRESOLVED CONTRADICTIONS ({len(unresolved)})")
            print(f"{'─'*50}")
            for c in unresolved:
                print(f"  ⚠️  [{c['severity'].upper()}] {c['name']}")
                print(f"      {c['description']}")
                print(f"      Question: {c.get('active_question', '')}")

        # ── Risk ──
        if results.get('risk') and results['risk'].get('status') == 'complete':
            risk = results['risk']
            print(f"\n{'─'*50}")
            print("RISK ASSESSMENT")
            print(f"{'─'*50}")
            print(f"  Overall Risk: {risk['metrics']['overall_risk'].upper()}")
            print(f"  Risks: {risk['metrics'].get('risk_count', 0)}, Warnings: {risk['metrics'].get('warning_count', 0)}")

        # ── Hypotheses Detail ──
        if hyp:
            print(format_hypotheses(hyp))

        print(f"\n{'='*60}")
        return 0

    # ═══════════════════════════════════════════════════════════════════════════
    # DEFAULT: Single-shot quant analysis (backward-compatible)
    # ═══════════════════════════════════════════════════════════════════════════

    run_quant_analysis(args.entity, show_sources=args.show_sources, period=args.period)
    return 0


if __name__ == "__main__":
    exit(main())