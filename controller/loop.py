
import json
import sqlite3
import logging
from typing import Dict, Callable, Any, Optional
from datetime import datetime, timezone

from utils.formatting import (
    phase_header, iteration_header, halt_banner,
    dashboard_panel, status, c,
    RED, GREEN, YELLOW, BLUE, CYAN, WHITE, BOLD, DIM
)
from data.db import DB_PATH
from core.evidence import EvidenceRegister
from agents.critic import CriticAgent
from reports.generator import generate_report
from data.audit import save_session

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 3


class EvidenceDrivenLoop:
    """
    Issue #9b+ Loop Controller.

    Usage:
        loop = EvidenceDrivenLoop(
            business_runner=lambda: run_business_analysis("AAPL", ticker="AAPL"),
            technical_runner=lambda: run_technical_analysis("apple/swift"),
            quant_agent=QuantAgent(),
            critic_agent=CriticAgent(),
            risk_agent=RiskAgent(),
            hypotheses_runner=generate_from_register,
        )
        results = loop.run(entity="AAPL", ticker="AAPL", repo="apple/swift", config={"hypotheses": True})
    """

    def __init__(self,
                 business_runner: Optional[Callable] = None,
                 technical_runner: Optional[Callable] = None,
                 quant_agent=None,
                 critic_agent=None,
                 risk_agent=None,
                 hypotheses_runner: Optional[Callable] = None,
                 ollama_client=None):
        self.db_path = str(DB_PATH)
        self.business_runner = business_runner
        self.technical_runner = technical_runner
        self.quant_agent = quant_agent
        self.critic_agent = critic_agent or CriticAgent(ollama_client=ollama_client)
        self.risk_agent = risk_agent
        self.hypotheses_runner = hypotheses_runner

        self.register = EvidenceRegister()
        self.iteration = 0
        self.halt_reason: Optional[str] = None
        self.asset_profile: Optional[dict] = None
        self.critic_history = []
        self.previous_critic_output: Optional[dict] = None
        self._ensure_table()

    def _ensure_table(self):
        """Ensure loop_states table exists with Issue #9b+ columns."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS loop_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    final_iteration INTEGER,
                    status TEXT CHECK(status IN ('running', 'completed', 'failed')),
                    critique_summary TEXT,
                    should_iterate_history TEXT,
                    halt_reason TEXT,
                    evidence_count INTEGER,
                    asset_type TEXT,
                    dashboard_history TEXT
                )
            """)
            # Add dashboard_history column if missing (migration)
            try:
                conn.execute("SELECT dashboard_history FROM loop_states LIMIT 1")
            except sqlite3.OperationalError:
                conn.execute("ALTER TABLE loop_states ADD COLUMN dashboard_history TEXT")
            conn.commit()

    def _persist(self, entity: str, status: str):
        """Persist loop state to SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM loop_states WHERE entity = ? AND status = 'running' ORDER BY id DESC LIMIT 1",
                (entity,)
            )
            row = cursor.fetchone()

            should_iter = json.dumps([c.get('halt_decision', {}).get('should_iterate', False) for c in self.critic_history])
            summary = self._summarize_critique()
            dashboards = json.dumps([c.get('dashboard', {}) for c in self.critic_history])
            now = datetime.now(timezone.utc).isoformat()

            if row:
                conn.execute(
                    """UPDATE loop_states 
                       SET completed_at = ?, final_iteration = ?, status = ?, 
                           critique_summary = ?, should_iterate_history = ?, 
                           halt_reason = ?, evidence_count = ?, asset_type = ?,
                           dashboard_history = ?
                       WHERE id = ?""",
                    (now, self.iteration, status, summary, should_iter,
                     self.halt_reason, len(self.register),
                     self.asset_profile.get("asset_type") if self.asset_profile else None,
                     dashboards, row[0])
                )
            else:
                conn.execute(
                    """INSERT INTO loop_states 
                       (entity, status, final_iteration, critique_summary, 
                        should_iterate_history, halt_reason, evidence_count, asset_type,
                        dashboard_history)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (entity, status, self.iteration, summary, should_iter,
                     self.halt_reason, len(self.register),
                     self.asset_profile.get("asset_type") if self.asset_profile else None,
                     dashboards)
                )
            conn.commit()

    def _summarize_critique(self) -> str:
        """Summarize latest critique for DB storage."""
        if not self.critic_history:
            return ""
        latest = self.critic_history[-1]
        halt = latest.get('halt_decision', {})
        dash = latest.get('dashboard', {})
        return (
            f"halt={not halt.get('should_iterate', True)}, "
            f"reason={halt.get('reason', 'unknown')}, "
            f"agreement={dash.get('agreement', {}).get('level', '?')}, "
            f"stability={dash.get('stability', {}).get('level', '?')}"
        )

    def run(self, entity: str, ticker: str = None, repo: str = None, 
            config: dict = None, sector: str = None) -> dict:
        """
        Main entry point. Executes the full evidence-driven pipeline.
        """
        config = config or {}
        ticker = ticker or entity

        print(f"\n{c('AIRS Evidence-Driven Loop', BOLD, CYAN)}  |  {c(entity, BOLD, WHITE)}")

        self._persist(entity, 'running')

        try:
            # Phase 0: Capability Probe
            self.asset_profile = self._probe_capabilities(entity, ticker, repo)
            self._display_profile(self.asset_profile)

            # Phase 1: Bootstrap
            self._bootstrap(entity, ticker, repo)

            # Phase 2: Iterative evidence accumulation
            self._iterative_loop(entity, ticker)

            # Phase 3: Final output generation
            results = self._final_output(entity, ticker, config)
            
            # Phase 9: Persist session to audit trail
            try:
                report_path = None
                if results.get('report'):
                    report_path = results['report'].get('markdown_path')
                session_id = save_session(results, report_path, sector=sector)
                results['session_id'] = session_id
            except Exception as e:
                logger.warning(f"Failed to save session to audit trail: {e}")

            self._persist(entity, 'completed')

            

            print(f"\n{c('OK Loop Complete', BOLD, GREEN)}  |  {self.iteration} iteration(s)  |  {len(self.register)} evidence items  |  {c(self.halt_reason, DIM)}")

            return results

        except Exception as e:
            self._persist(entity, 'failed')
            logger.exception(f"Loop failed for {entity}")
            raise

    def _probe_capabilities(self, entity: str, ticker: Optional[str], repo: Optional[str]) -> dict:
        """Phase 0: Capability Probe. Detects available dimensions."""
        print(phase_header(0, "Capability Probe"))

        profile = {
            "entity": entity,
            "ticker": None,
            "repo": None,
            "quant_available": False,
            "technical_available": False,
            "business_available": True,
            "asset_type": "unknown",
        }

        probe_ticker = ticker or entity
        try:
            import yfinance as yf
            info = yf.Ticker(probe_ticker).info
            if info and info.get("regularMarketPrice") is not None:
                profile["quant_available"] = True
                profile["ticker"] = probe_ticker
                print(status(c("OK", GREEN), "Quant", f"ticker '{probe_ticker}' resolved"))
            else:
                print(status(c("X", DIM), "Quant", f"no market data for '{probe_ticker}'"))
        except Exception as e:
            print(status(c("X", DIM), "Quant", f"unavailable: {str(e)[:60]}"))

        if repo:
            try:
                import requests
                r = requests.get(f"https://api.github.com/repos/{repo}", timeout=5)
                if r.status_code == 200:
                    profile["technical_available"] = True
                    profile["repo"] = repo
                    print(status(c("OK", GREEN), "Technical", f"repo '{repo}' found"))
                else:
                    print(status(c("X", DIM), "Technical", f"GitHub returned {r.status_code}"))
            except Exception as e:
                print(status(c("X", DIM), "Technical", f"unavailable: {str(e)[:60]}"))
        else:
            print(status(c("~", DIM), "Technical", "no repo provided, skipping probe"))

        if profile["quant_available"] and profile["technical_available"]:
            profile["asset_type"] = "public_stock_with_repo"
        elif profile["quant_available"]:
            profile["asset_type"] = "public_stock"
        elif profile["technical_available"]:
            profile["asset_type"] = "open_source_or_pre_launch"
        else:
            profile["asset_type"] = "private_company"

        print(status(c("->", BLUE), "Asset type", profile['asset_type']))
        return profile

    def _display_profile(self, profile: dict):
        """Display capability probe results."""
        dims = []
        if profile.get("quant_available"): dims.append("Quant")
        if profile.get("technical_available"): dims.append("Technical")
        if profile.get("business_available"): dims.append("Business")
        print(f"  Available dimensions: {', '.join(dims) if dims else 'None'}")

    def _bootstrap(self, entity: str, ticker: str, repo: str) -> None:
        """Phase 1: Bootstrap. Business and Technical run ONCE."""
        print(phase_header(1, "Bootstrap (Business + Technical)"))

        if self.business_runner:
            print(status(">", "Business", f"analyzing {entity}..."))
            try:
                business_output = self.business_runner()
                self.register.add("business_context", business_output, source="business")
                biz_status = business_output.get("status", "unknown")
                articles = business_output.get("metrics", {}).get("signal_count", 0)
                print(status(c("OK", GREEN), "Business", f"{articles} signals -> Evidence Register"))
            except Exception as e:
                print(status(c("!", YELLOW), "Business", f"failed: {e}"))
                self.register.add("business_context", {
                    "status": "failed", "error": str(e), "confidence": 0.0
                }, source="business")
        else:
            print("  Business runner not configured - skipping")

        if self.technical_runner and self.asset_profile.get("technical_available"):
            print(status(">", "Technical", "analyzing..."))
            try:
                technical_output = self.technical_runner()
                if technical_output:
                    self.register.add("technical_context", technical_output, source="technical")
                    tech_status = technical_output.get("status", "unknown")
                    print(status(c("OK", GREEN), "Technical", f"{tech_status} -> Evidence Register"))
                else:
                    print(status(c("~", DIM), "Technical", "runner returned None - skipping"))
            except Exception as e:
                print(status(c("!", YELLOW), "Technical", f"failed: {e}"))
                self.register.add("technical_context", {
                    "status": "failed", "error": str(e), "confidence": 0.0
                }, source="technical")
        else:
            if not self.asset_profile.get("technical_available"):
                print(status(c("~", DIM), "Technical", "unavailable for this asset type -> skipped"))
            else:
                print("  Technical runner not configured - skipping")

        print(status(c("OK", GREEN), "Bootstrap complete", f"{len(self.register)} evidence items"))

    def _iterative_loop(self, entity: str, ticker: str) -> None:
        """Phase 2: Iterative Evidence Accumulation (iteration-aware)."""
        print(phase_header(2, "Iterative Evidence Accumulation"))

        for i in range(MAX_ITERATIONS):
            self.iteration = i + 1
            print(iteration_header(self.iteration, MAX_ITERATIONS))

            # Determine tier and data depth
            tier = self._determine_tier()
            period = self._get_tier_period(tier)
            print(status(">", f"Quant Tier {tier}", f"{period} data depth"))

            # Run quant agent
            if self.quant_agent and self.asset_profile.get("quant_available"):
                try:
                    quant_output = self.quant_agent.run(
                        ticker=ticker,
                        tier=tier,
                        evidence_register=self.register
                    )

                    new_features = []
                    for key, value in quant_output.items():
                        if key.startswith("_"):
                            continue

                        data_points = None
                        if key == "price_data" and hasattr(value, '__len__'):
                            data_points = len(value)
                        elif key != "price_data":
                            if "price_data" in quant_output and hasattr(quant_output["price_data"], '__len__'):
                                data_points = len(quant_output["price_data"])

                        self.register.add(
                            key, value, source="quant", tier=tier,
                            data_points=data_points, data_period=period
                        )
                        new_features.append(key)

                    if new_features:
                        print(status(c("OK", GREEN), f"Quant Tier {tier}", f"upgraded {len(new_features)} features"))
                    else:
                        print(status(c("~", DIM), f"Quant Tier {tier}", "no new features"))

                except Exception as e:
                    print(status(c("!", YELLOW), "Quant", f"failed: {e}"))
            else:
                if not self.asset_profile.get("quant_available"):
                    print(status(c("~", DIM), "Quant", "unavailable for this asset type -> skipped"))
                else:
                    print("  Quant agent not configured - skipping")

            # Run critic (with previous output for stability tracking)
            print(status(">", "Critic", "evaluating evidence..."))
            try:
                critic_output = self.critic_agent.evaluate_evidence(
                    entity=entity,
                    evidence_register=self.register,
                    asset_profile=self.asset_profile,
                    iteration=self.iteration,
                    previous_critic_output=self.previous_critic_output,
                )
                self.critic_history.append(critic_output)
                self._display_critic(critic_output)

            except Exception as e:
                print(status(c("!", YELLOW), "Critic", f"failed: {e}"))
                critic_output = {
                    "halt_decision": {"should_iterate": False, "reason": "critic_error", "recommendation": "insufficient_halt"},
                    "dashboard": {},
                    "active_questions": [],
                }

            # Store for next iteration's stability comparison
            self.previous_critic_output = critic_output

            # Halt check
            halt = critic_output.get("halt_decision", {})
            if not halt.get("should_iterate", True):
                self.halt_reason = halt.get("reason", "unknown")
                narrative = halt.get("narrative", "Halting.")
                print(halt_banner(self.halt_reason, narrative, circuit=False))
                break

            # Circuit breaker
            if self.iteration >= MAX_ITERATIONS:
                self.halt_reason = "max_iterations"
                print(halt_banner("max_iterations", f"Circuit breaker ({MAX_ITERATIONS} iterations)", circuit=True))
                break

            # Continue to next tier
            print(f"   {c('Continuing to next tier...', DIM)}")

        print(status(c("*", BLUE), "Loop ended", f"{self.iteration} iterations | {len(self.register)} evidence items"))

    def _determine_tier(self) -> int:
        return self.iteration

    def _get_tier_period(self, tier: int) -> str:
        periods = {1: "3mo", 2: "6mo", 3: "1y"}
        return periods.get(tier, "3mo")

    def _display_critic(self, result: dict):
        """Display critic audit results - compact dashboard."""
        dash = result.get("dashboard", {})
        halt = result.get("halt_decision", {})
        dq = dash.get("data_quality", {})
        cov = dash.get("coverage", {})
        agr = dash.get("agreement", {})
        stab = dash.get("stability", {})

        print(dashboard_panel(
            dq.get('score', 0),
            cov.get('score', 0),
            agr.get('level', 'Unknown'),
            stab.get('level', 'Unknown')
        ))

        questions = result.get("active_questions", [])
        if questions:
            print(f"\n{c(f'Active Questions: {len(questions)}', BOLD)}")
            for q in questions:
                icon = c(">", CYAN) if q.get('can_deeper_data_answer') else c("?", YELLOW)
                print(f"  {icon} {c(q['question'], BOLD)}")
                print(f"     {c(q.get('why_it_matters', ''), DIM)}")

        unresolved = result.get("unresolved_contradictions", [])
        if unresolved:
            print(f"\n{c(f'Contradictions: {len(unresolved)}', BOLD, RED)}")
            for c_item in unresolved:
                sev_color = RED if c_item.get('severity') == 'high' else YELLOW
                print(f"  {c('!', sev_color)}  [{c(c_item['severity'].upper(), BOLD, sev_color)}] {c_item['name']}")
                print(f"     {c(c_item['description'], DIM)}")

        rec = halt.get('recommendation', 'unknown').upper()
        rec_color = GREEN if rec == 'COMPLETE' else YELLOW
        print(f"\n{c('Decision:', BOLD)} {c(rec, BOLD, rec_color)}  |  {c(halt.get('reason', ''), DIM)}")
        if halt.get('narrative'):
            print(f"   {c(halt['narrative'], DIM)}")

    def _final_output(self, entity: str, ticker: str, config: dict) -> dict:
        """Phase 3: Final Output Generation."""
        print(phase_header(3, "Final Output Generation"))

        agent_outputs = self._build_legacy_agent_outputs()

        # Risk Agent
        risk_output = None
        if self.risk_agent:
            print(status(">", "Risk Assessment", "analyzing..."))
            try:
                risk_output = self.risk_agent.analyze(entity=entity, agent_outputs=agent_outputs)
                overall = risk_output.get('metrics', {}).get('overall_risk', 'unknown')
                r_color = RED if overall == 'high' else YELLOW if overall == 'medium' else GREEN
                print(status(c("OK", r_color), "Risk", f"{overall.upper()}"))
            except Exception as e:
                print(status(c("!", YELLOW), "Risk", f"failed: {e}"))
                risk_output = {"status": "failed", "error": str(e)}

        # Hypotheses
        hypotheses_output = None
        if config.get('hypotheses') and self.hypotheses_runner:
            print(status(">", "Hypotheses", "generating..."))
            try:
                hypotheses_output = self.hypotheses_runner(entity, self.register)
                from reports.hypothesis import format_hypotheses
                print(format_hypotheses(hypotheses_output))
            except Exception as e:
                print(status(c("!", YELLOW), "Hypotheses", f"failed: {e}"))
                hypotheses_output = {"status": "failed", "error": str(e)}

        # Compile final results
        latest_critic = self.critic_history[-1] if self.critic_history else {}
        dash = latest_critic.get("dashboard", {})

        # Generate investment memo (Issue #10)
        report_output = None
        if config.get('hypotheses'):
            print(status(">", "Report", "generating investment memo..."))
            try:
                report_output = generate_report(
                    {
                        "entity": entity,
                        "ticker": ticker,
                        "asset_type": self.asset_profile.get("asset_type") if self.asset_profile else "unknown",
                        "iterations": self.iteration,
                        "halt_reason": self.halt_reason,
                        "evidence_count": len(self.register),
                        "evidence_snapshot": self.register.snapshot(exclude_types=("DataFrame",)),
                        "dashboard": latest_critic.get("dashboard", {}),
                        "hypotheses": hypotheses_output,
                        "risk": risk_output,
                        "active_questions": latest_critic.get("active_questions", []),
                        "unresolved_contradictions": latest_critic.get("unresolved_contradictions", []),
                        "evidence_by_source": {
                            "business": list(self.register.list_by_source("business").keys()),
                            "technical": list(self.register.list_by_source("technical").keys()),
                            "quant": list(self.register.list_by_source("quant").keys()),
                        },
                        "evidence_by_tier": {
                            1: list(self.register.list_by_tier(1).keys()),
                            2: list(self.register.list_by_tier(2).keys()),
                            3: list(self.register.list_by_tier(3).keys()),
                        },
                    },
                    output_dir=config.get("report_dir", "reports/output"),
                    pdf=config.get("pdf", False),
                )
                print(status(c("OK", GREEN), "Report saved", str(report_output['markdown_path'])))
                if report_output['pdf_path']:
                    print(status(c("OK", GREEN), "PDF saved", str(report_output['pdf_path'])))
            except Exception as e:
                print(status(c("!", YELLOW), "Report", f"failed: {e}"))

        results = {
            "entity": entity,
            "ticker": ticker,
            "asset_type": self.asset_profile.get("asset_type") if self.asset_profile else "unknown",
            "asset_profile": self.asset_profile,
            "iterations": self.iteration,
            "halt_reason": self.halt_reason,
            "evidence_count": len(self.register),
            "evidence_keys": self.register.keys(),
            "evidence_by_source": {
                "business": list(self.register.list_by_source("business").keys()),
                "technical": list(self.register.list_by_source("technical").keys()),
                "quant": list(self.register.list_by_source("quant").keys()),
            },
            "evidence_by_tier": {
                1: list(self.register.list_by_tier(1).keys()),
                2: list(self.register.list_by_tier(2).keys()),
                3: list(self.register.list_by_tier(3).keys()),
            },

            # NEW: Dashboard-driven outputs
            "dashboard": dash,
            "active_questions": latest_critic.get("active_questions", []),
            "missing_evidence": latest_critic.get("missing_evidence", []),
            "unavailable_dimensions": latest_critic.get("impossible_dimensions", []),
            "resolvable_contradictions": latest_critic.get("resolvable_contradictions", []),
            "unresolved_contradictions": latest_critic.get("unresolved_contradictions", []),
            "final_confidence": latest_critic.get("confidence", 0.0),

            # Legacy
            "risk": risk_output,
            "hypotheses": hypotheses_output,
            "agent_outputs": agent_outputs,
            "evidence_snapshot": self.register.snapshot(exclude_types=("DataFrame",)),
            "critic_history": self.critic_history,
            "report": report_output,
        }

        return results

    def _build_legacy_agent_outputs(self) -> dict:
        """Construct legacy agent_outputs dict from Evidence Register."""
        agent_outputs = {}

        if self.register.has("business_context"):
            biz = self.register.get("business_context")
            agent_outputs["business"] = biz if isinstance(biz, dict) else {
                "status": "complete", "data": biz, "confidence": 0.8
            }

        if self.register.has("technical_context"):
            tech = self.register.get("technical_context")
            agent_outputs["technical"] = tech if isinstance(tech, dict) else {
                "status": "complete", "data": tech, "confidence": 0.8
            }

        quant_metrics = self.register.list_by_source("quant")
        if quant_metrics:
            safe_metrics = {k: v for k, v in quant_metrics.items()
                          if not hasattr(v, 'to_dict') and not k.startswith("_")}
            agent_outputs["quant"] = {
                "status": "complete",
                "metrics": safe_metrics,
                "confidence": 0.85,
                "ticker": self.asset_profile.get("ticker", "unknown") if self.asset_profile else "unknown",
            }

        return agent_outputs