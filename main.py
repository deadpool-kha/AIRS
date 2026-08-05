import argparse
import pandas as pd

from utils.formatting import (
    header, box, mini_box, progress_bar, status,
    dashboard_panel, bias_panel, uncertainty_panel,
    question_line, contradiction_line, report_footer, c,
    RED, GREEN, YELLOW, BLUE, CYAN, MAGENTA, BOLD, DIM, RESET
)
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
    parser.add_argument("--pdf", action="store_true", help="Also generate PDF report (requires weasyprint)")
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
        print(header("AIRS", "v0.3.7", "Evidence-Driven Investment Research"))
        

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
                'pdf': args.pdf,
            }
        )

        # ═══════════════════════════════════════════════════════════════════════
        # FINAL RESULTS SUMMARY — DASHBOARD STYLE
        # ═══════════════════════════════════════════════════════════════════════

                # COMPACT FINAL SUMMARY - Unicode boxes + ANSI colors
        print("\n")

        # Meta
        dims = []
        if results.get('asset_profile', {}).get('quant_available'): dims.append("Quant")
        if results.get('asset_profile', {}).get('technical_available'): dims.append("Technical")
        if results.get('asset_profile', {}).get('business_available'): dims.append("Business")
        print(status("*", f"Entity: {results['entity']}", f"Dimensions: {' * '.join(dims) if dims else 'None'}"))
        print(status("*", f"Iterations: {results['iterations']}", f"Halt: {results['halt_reason']}"))
        print(status("*", f"Evidence: {results['evidence_count']} items"))

        # Dashboard
        dash = results.get('dashboard', {})
        if dash:
            dq = dash.get('data_quality', {})
            cov = dash.get('coverage', {})
            agr = dash.get('agreement', {})
            stab = dash.get('stability', {})
            print(dashboard_panel(
                dq.get('score', 0),
                cov.get('score', 0),
                agr.get('level', 'Unknown'),
                stab.get('level', 'Unknown')
            ))

        # Bias + Uncertainty
        hyp = results.get('hypotheses', {})
        if hyp:
            bias = hyp.get('directional_bias', {})
            unc = hyp.get('uncertainty', {})
            if bias:
                print(bias_panel(
                    bias.get('net', 'unknown'),
                    bias.get('bull_strength', 0),
                    bias.get('bear_strength', 0),
                    bias.get('directional_score', 0)
                ))
            if unc:
                fac = unc.get('factors', {})
                print(uncertainty_panel(
                    unc.get('level', 'Unknown'),
                    unc.get('score', 0),
                    fac.get('scarcity', 0),
                    fac.get('conflict', 0),
                    fac.get('coverage', 0)
                ))

        # Active Questions
        questions = results.get('active_questions', [])
        if questions:
            print(f"\n{c(f'Active Questions: {len(questions)}', BOLD)}")
            for i, q in enumerate(questions, 1):
                print(question_line(
                    i, q['question'],
                    q.get('why_it_matters', ''),
                    q.get('can_deeper_data_answer', False)
                ))

        # Contradictions
        unresolved = results.get('unresolved_contradictions', [])
        if unresolved:
            print(f"\n{c(f'Unresolved Contradictions: {len(unresolved)}', BOLD, RED)}")
            for c_item in unresolved:
                print(contradiction_line(
                    c_item['name'],
                    c_item['description'],
                    c_item.get('severity', 'medium')
                ))

        # Risk
        if results.get('risk') and results['risk'].get('status') == 'complete':
            risk = results['risk']
            overall = risk['metrics'].get('overall_risk', 'unknown').upper()
            r_color = RED if overall == 'HIGH' else YELLOW if overall == 'MEDIUM' else GREEN
            print(f"\n{c('Overall Risk:', BOLD)} {c(overall, BOLD, r_color)}")
            print(f"  Risks: {risk['metrics'].get('risk_count', 0)}  |  Warnings: {risk['metrics'].get('warning_count', 0)}")

        # Report path
        report = results.get('report')
        if report:
            md_path = str(report.get('markdown_path', ''))
            pdf_path = str(report.get('pdf_path', '')) if report.get('pdf_path') else None
            print(report_footer(md_path, pdf_path))

        # Detailed hypotheses (legacy, still useful)
        
        return 0

    # ═══════════════════════════════════════════════════════════════════════════
    # DEFAULT: Single-shot quant analysis (backward-compatible)
    # ═══════════════════════════════════════════════════════════════════════════

    run_quant_analysis(args.entity, show_sources=args.show_sources, period=args.period)
    return 0


if __name__ == "__main__":
    exit(main())