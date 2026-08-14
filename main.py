import argparse
import json
from pathlib import Path
import pandas as pd

from config.sectors import normalize_sector, list_sectors
from data.audit import get_accuracy_stats, record_outcome
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


def load_watchlist(category: str):
    """Load entities from config/watchlist.json."""
    watchlist_path = Path(__file__).parent / "config" / "watchlist.json"
    with open(watchlist_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    from config.sectors import validate_watchlist_sectors
    validate_watchlist_sectors(data)
    
    if category == "all":
        all_entities = []
        for cat, entities in data["watchlists"].items():
            all_entities.extend(entities)
        return all_entities
    
    if category not in data["watchlists"]:
        available = list(data["watchlists"].keys())
        raise ValueError(f"Unknown watchlist: '{category}'. Available: {available}")
    
    return data["watchlists"][category]


def run_audit(force=False):
    """Run the audit trail: evaluate historical sessions and display stats."""
    from datetime import datetime, timedelta, timezone
    from data.db import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    
    if force:
        cursor.execute("DELETE FROM research_outcomes")
        conn.commit()
        print("Cleared all existing outcomes for forced re-evaluation.")
        cursor.execute("SELECT id, ticker FROM research_sessions WHERE ticker IS NOT NULL")
    else:
        cursor.execute("""
            SELECT id, ticker FROM research_sessions 
            WHERE ticker IS NOT NULL 
            AND session_date <= ?
            AND id NOT IN (SELECT session_id FROM research_outcomes)
        """, (thirty_days_ago,))
    
    pending = cursor.fetchall()
    conn.close()
    
    print(f"\n{'='*60}")
    print("AIRS AUDIT TRAIL")
    print(f"{'='*60}")
    
    if not pending:
        print("No pending sessions to evaluate.")
    else:
        print(f"Evaluating {len(pending)} session(s)...")
        for row in pending:
            result = record_outcome(row["id"], row["ticker"])
            status = result.get("status", "unknown")
            if status == "recorded":
                print(f"  Session {row['id']}: {result['actual_direction']} {result['price_change_30d']:+.2f}% (score: {result['accuracy_score']:+.2f})")
            elif status == "pending":
                print(f"  Session {row['id']}: pending (not old enough)")
            else:
                print(f"  Session {row['id']}: {status} - {result.get('reason', 'unknown')}")
    
    # Display stats
    stats = get_accuracy_stats()
    print(f"\n{'='*60}")
    print("ACCURACY STATISTICS")
    print(f"{'='*60}")
    print(f"Total sessions:      {stats['total_sessions']}")
    print(f"Scored sessions:     {stats['scored_sessions']}")
    print(f"Pending evaluation:  {stats['pending_sessions']}")
    print(f"Overall avg score:   {stats['overall_avg_score']:+.4f}")
    
    if stats['by_asset_type']:
        print(f"\nBy Asset Type:")
        for asset_type, data in sorted(stats['by_asset_type'].items()):
            print(f"  {asset_type:20s} | {data['count']:3d} sessions | avg: {data['avg_score']:+.4f}")
    
    if stats['by_uncertainty']:
        print(f"\nBy Uncertainty Level:")
        for level, data in sorted(stats['by_uncertainty'].items()):
            print(f"  {level:20s} | {data['count']:3d} sessions | avg: {data['avg_score']:+.4f}")
    
    if stats['by_evidence_strength']:
        print(f"\nBy Evidence Strength:")
        for strength, data in sorted(stats['by_evidence_strength'].items()):
            if data['count'] > 0:
                print(f"  {strength:20s} | {data['count']:3d} sessions | avg: {data['avg_score']:+.4f}")
    
    if stats['by_sector']:
        print(f"\nBy Sector:")
        for sector, data in sorted(stats['by_sector'].items()):
            print(f"  {sector:20s} | {data['count']:3d} sessions | avg: {data['avg_score']:+.4f}")
    
    print(f"{'='*60}")

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
    parser.add_argument("--watchlist", type=str, help="Batch analyze watchlist category (e.g., 'tech_blue_chip', 'all')")
    parser.add_argument("--sector", type=str, help="Sector tag for audit trail (e.g., 'semiconductors')")
    parser.add_argument("--list-sectors", action="store_true", help="List valid sectors and exit")
    parser.add_argument("--list-sessions", action="store_true", help="List all research sessions and exit")
    parser.add_argument("--audit", action="store_true", help="Run audit trail: evaluate historical sessions")
    parser.add_argument("--audit-force", action="store_true", help="Force re-evaluation of all historical sessions")
    args = parser.parse_args()

       # Validate inputs
    if not args.technical_only and not args.entity and not args.watchlist and not args.audit and not args.list_sectors and not args.list_sessions:
        parser.error("--entity is required unless using --technical-only, --watchlist, --audit, or --list-sectors")

    if args.technical_only and not args.repo and not args.watchlist:
        parser.error("--repo is required when using --technical-only")

    if args.risk_only:
        parser.error("--risk-only is not supported. Use --hypotheses for full analysis.")

    # --list-sectors: early exit
        
    if args.list_sessions:
        from data.db import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, entity, ticker, sector, session_date, directional_bias,
                   uncertainty_level, iterations, evidence_count, halt_reason
            FROM research_sessions
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        print(f"\n{'='*90}")
        print("RESEARCH SESSIONS")
        print(f"{'='*90}")
        if not rows:
            print("No sessions found.")
        else:
            print(f"{'ID':<4} {'Entity':<14} {'Ticker':<10} {'Sector':<18} {'Date':<12} {'Bias':<8} {'Uncert':<10} {'Iters':<5} {'Evidence':<8}")
            print("-" * 90)
            for r in rows:
                ticker = r['ticker'] or '-'
                sector = r['sector'] or '-'
                print(f"{r['id']:<4} {r['entity']:<14} {ticker:<10} {sector:<18} {r['session_date']:<12} {r['directional_bias']:<8} {r['uncertainty_level']:<10} {r['iterations']:<5} {r['evidence_count']:<8}")
        print(f"{'='*90}")
        print(f"Total: {len(rows)} session(s)")
        return 0

    # Validate sector if provided
    if args.sector:
        canonical = normalize_sector(args.sector)
        if canonical is None:
            print(f"Error: Unknown sector '{args.sector}'.")
            print("Run 'python main.py --list-sectors' to see valid options.")
            return 1
        args.sector = canonical  # Replace with canonical form

    # Watchlist mode implies hypotheses
    if args.watchlist:
        args.hypotheses = True

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
    # AUDIT MODE
    # ═══════════════════════════════════════════════════════════════════════════

    if args.audit:
        run_audit(force=args.audit_force)
        return 0

    # ═══════════════════════════════════════════════════════════════════════════
    # BATCH / WATCHLIST MODE
    # ═══════════════════════════════════════════════════════════════════════════

    if args.watchlist:
        print(header("AIRS", "v0.3.7", f"Batch Analysis: {args.watchlist}"))
        
        try:
            entities = load_watchlist(args.watchlist)
        except ValueError as e:
            print(f"Error: {e}")
            return 1
        
        print(f"Loaded {len(entities)} entities from watchlist '{args.watchlist}'\n")
        
        batch_results = []
        
        for item in entities:
            entity = item["entity"]
            ticker = item.get("ticker")
            repo = item.get("repo")
            sector = item.get("sector")
            
            print(f"\n{'='*60}")
            print(f"ANALYZING: {entity}")
            print(f"{'='*60}")
            
            quant_agent = QuantAgent()
            critic_agent = CriticAgent()
            risk_agent = RiskAgent()
            
            loop = EvidenceDrivenLoop(
                business_runner=lambda e=entity, t=ticker: run_business_analysis(e, ticker=t),
                technical_runner=(lambda r=repo: run_technical_analysis(r)) if repo else None,
                quant_agent=quant_agent,
                critic_agent=critic_agent,
                risk_agent=risk_agent,
                hypotheses_runner=generate_from_register,
            )
            
            results = loop.run(
                entity=entity,
                ticker=ticker or entity,
                repo=repo,
                config={
                    'hypotheses': True,
                    'show_sources': args.show_sources,
                    'pdf': args.pdf,
                },
                sector=sector,
            )
            
            batch_results.append({
                "entity": entity,
                "ticker": ticker,
                "sector": sector,
                "bias": results.get("hypotheses", {}).get("directional_bias", {}).get("net", "unknown"),
                "uncertainty": results.get("hypotheses", {}).get("uncertainty", {}).get("level", "Unknown"),
                "iterations": results.get("iterations", 0),
                "evidence_count": results.get("evidence_count", 0),
                "session_id": results.get("session_id"),
            })
        
        # Batch summary
        print(f"\n{'='*60}")
        print("BATCH SUMMARY")
        print(f"{'='*60}")
        print(f"{'Entity':<20} {'Ticker':<10} {'Bias':<10} {'Uncertainty':<12} {'Iters':<6} {'Evidence':<8}")
        print("-" * 60)
        for r in batch_results:
            ticker_str = r["ticker"] or "-"
            print(f"{r['entity']:<20} {ticker_str:<10} {r['bias']:<10} {r['uncertainty']:<12} {r['iterations']:<6} {r['evidence_count']:<8}")
        print(f"{'='*60}")
        
        return 0

    # ═══════════════════════════════════════════════════════════════════════════
    # EVIDENCE-DRIVEN LOOP MODE (single entity)
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
            },
            sector=args.sector,
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