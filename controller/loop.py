"""
controller/loop.py
Issue #9b+: Evidence-Driven Loop Evolution

Replaces the treadmill loop with a convergent evidence accumulation pattern.

Architecture:
    1. CAPABILITY PROBE: Detect which dimensions are available
    2. BOOTSTRAP: Business + Technical run ONCE → Evidence Register
    3. ITERATE: Quant runs tiered computation. Critic asks different questions per iteration:
       Iteration 1: "Can I form a coherent directional view?"
       Iteration 2: "Did deeper data change the story?"
       Iteration 3: Circuit breaker
    4. HALT: Dashboard-driven (coherent view, stable thesis, or max iterations)
    5. OUTPUT: Risk + Hypotheses synthesize from final Evidence Register state

Key changes:
    - Critic now receives previous_critic_output for stability tracking
    - Loop stores dashboard history in SQLite
    - Display shows Data Quality / Coverage / Agreement / Stability dashboard
    - Hypotheses render directional bias + uncertainty
"""

import json
import sqlite3
import logging
from typing import Dict, Callable, Any, Optional
from datetime import datetime, timezone

from data.db import DB_PATH
from core.evidence import EvidenceRegister
from agents.critic import CriticAgent

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

    def run(self, entity: str, ticker: str = None, repo: str = None, config: dict = None) -> dict:
        """
        Main entry point. Executes the full evidence-driven pipeline.
        """
        config = config or {}
        ticker = ticker or entity

        print(f"\n{'='*60}")
        print(f"AIRS EVIDENCE-DRIVEN LOOP: {entity}")
        print(f"{'='*60}")

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

            self._persist(entity, 'completed')

            print(f"\n{'='*60}")
            print(f"LOOP COMPLETE: {self.iteration} iterations | {len(self.register)} evidence items")
            print(f"Asset type: {self.asset_profile.get('asset_type', 'unknown')}")
            print(f"Halt reason: {self.halt_reason}")
            print(f"{'='*60}")

            return results

        except Exception as e:
            self._persist(entity, 'failed')
            logger.exception(f"Loop failed for {entity}")
            raise

    def _probe_capabilities(self, entity: str, ticker: Optional[str], repo: Optional[str]) -> dict:
        """Phase 0: Capability Probe. Detects available dimensions."""
        print(f"\n{'─'*50}")
        print("PHASE 0: CAPABILITY PROBE")
        print(f"{'─'*50}")

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
                print(f"  ✓ Quant available: ticker '{probe_ticker}' resolved")
            else:
                print(f"  ✗ Quant unavailable: no market data for '{probe_ticker}'")
        except Exception as e:
            print(f"  ✗ Quant unavailable: {str(e)[:60]}")

        if repo:
            try:
                import requests
                r = requests.get(f"https://api.github.com/repos/{repo}", timeout=5)
                if r.status_code == 200:
                    profile["technical_available"] = True
                    profile["repo"] = repo
                    print(f"  ✓ Technical available: repo '{repo}' found")
                else:
                    print(f"  ✗ Technical unavailable: GitHub returned {r.status_code}")
            except Exception as e:
                print(f"  ✗ Technical unavailable: {str(e)[:60]}")
        else:
            print(f"  ~ Technical: no repo provided, skipping probe")

        if profile["quant_available"] and profile["technical_available"]:
            profile["asset_type"] = "crypto_with_repo"
        elif profile["quant_available"]:
            profile["asset_type"] = "public_stock"
        elif profile["technical_available"]:
            profile["asset_type"] = "open_source_or_pre_launch"
        else:
            profile["asset_type"] = "private_company"

        print(f"  → Asset type: {profile['asset_type']}")
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
        print(f"\n{'─'*50}")
        print("PHASE 1: BOOTSTRAP (Business + Technical)")
        print(f"{'─'*50}")

        if self.business_runner:
            print(f"→ Running business analysis for {entity}...")
            try:
                business_output = self.business_runner()
                self.register.add("business_context", business_output, source="business")
                status = business_output.get("status", "unknown")
                articles = business_output.get("metrics", {}).get("signal_count", 0)
                print(f"  Business: {status} ({articles} signals) → Evidence Register")
            except Exception as e:
                print(f"  ⚠️  Business agent failed: {e}")
                self.register.add("business_context", {
                    "status": "failed", "error": str(e), "confidence": 0.0
                }, source="business")
        else:
            print("  Business runner not configured — skipping")

        if self.technical_runner and self.asset_profile.get("technical_available"):
            print(f"→ Running technical analysis...")
            try:
                technical_output = self.technical_runner()
                if technical_output:
                    self.register.add("technical_context", technical_output, source="technical")
                    status = technical_output.get("status", "unknown")
                    print(f"  Technical: {status} → Evidence Register")
                else:
                    print("  Technical runner returned None — skipping")
            except Exception as e:
                print(f"  ⚠️  Technical agent failed: {e}")
                self.register.add("technical_context", {
                    "status": "failed", "error": str(e), "confidence": 0.0
                }, source="technical")
        else:
            if not self.asset_profile.get("technical_available"):
                print("  Technical: unavailable for this asset type → skipped")
            else:
                print("  Technical runner not configured — skipping")

        print(f"  Bootstrap complete. Register has {len(self.register)} items.")

    def _iterative_loop(self, entity: str, ticker: str) -> None:
        """Phase 2: Iterative Evidence Accumulation (iteration-aware)."""
        print(f"\n{'─'*50}")
        print("PHASE 2: ITERATIVE EVIDENCE ACCUMULATION")
        print(f"{'─'*50}")

        for i in range(MAX_ITERATIONS):
            self.iteration = i + 1
            print(f"\n{'─'*40}")
            print(f"ITERATION {self.iteration}/{MAX_ITERATIONS}")
            print(f"{'─'*40}")

            # Determine tier and data depth
            tier = self._determine_tier()
            period = self._get_tier_period(tier)
            print(f"→ Quant Tier {tier} ({period} data depth)")

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
                        print(f"  Quant tier {tier} added/upgraded: {new_features}")
                    else:
                        print(f"  Quant tier {tier}: nothing new to compute")

                except Exception as e:
                    print(f"  ⚠️  Quant agent failed: {e}")
            else:
                if not self.asset_profile.get("quant_available"):
                    print("  Quant: unavailable for this asset type → skipped")
                else:
                    print("  Quant agent not configured — skipping")

            # Run critic (with previous output for stability tracking)
            print(f"→ Running evidence audit...")
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
                print(f"  ⚠️  Critic failed: {e}")
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
                print(f"\n✅ HALT: {narrative}")
                break

            # Circuit breaker
            if self.iteration >= MAX_ITERATIONS:
                self.halt_reason = "max_iterations"
                print(f"\n⛔ HALT: Circuit breaker hit ({MAX_ITERATIONS} iterations)")
                break

            # Continue to next tier
            print(f"   {halt.get('narrative', 'Continuing to next tier.')}")

        print(f"\n  Loop ended: {self.iteration} iterations, {len(self.register)} evidence items")

    def _determine_tier(self) -> int:
        return self.iteration

    def _get_tier_period(self, tier: int) -> str:
        periods = {1: "3mo", 2: "6mo", 3: "1y"}
        return periods.get(tier, "3mo")

    def _display_critic(self, result: dict):
        """Display critic audit results — DASHBOARD STYLE."""
        print(f"\n{'='*50}")
        print(f"EVIDENCE AUDIT (Iteration {result['iteration']})")
        print(f"{'='*50}")

        dash = result.get("dashboard", {})
        halt = result.get("halt_decision", {})

        # Dashboard
        dq = dash.get("data_quality", {})
        cov = dash.get("coverage", {})
        agr = dash.get("agreement", {})
        stab = dash.get("stability", {})

        print(f"Asset type: {result['asset_type']}")
        print(f"Data Quality:  {dq.get('score', 0):.0%}")
        print(f"Coverage:      {cov.get('score', 0):.0%} ({cov.get('present', 0)}/{cov.get('required', 0)} features)")
        print(f"Agreement:     {agr.get('level', '?')} ({agr.get('details', '')})")
        print(f"Stability:     {stab.get('level', '?')} — {stab.get('details', '')}")

        # Active questions
        questions = result.get("active_questions", [])
        if questions:
            print(f"\nActive Questions ({len(questions)}):")
            for q in questions:
                print(f"  ? {q['question']}")
                print(f"    Why: {q['why_it_matters']}")
                if q.get('can_deeper_data_answer'):
                    print(f"    → Deeper data may answer this")
                else:
                    print(f"    → Deeper data will NOT help; flag for human review")

        # Contradictions
        unresolved = result.get("unresolved_contradictions", [])
        if unresolved:
            print(f"\nUnresolved Contradictions ({len(unresolved)}):")
            for c in unresolved:
                print(f"  ⚠️  [{c['severity'].upper()}] {c['name']}: {c['description']}")

        # Decision
        print(f"\nDecision: {halt.get('recommendation', 'unknown').upper()}")
        print(f"Reason:   {halt.get('reason', 'unknown')}")
        print(f"Narrative: {halt.get('narrative', '')}")
        print(f"{'='*50}")

    def _final_output(self, entity: str, ticker: str, config: dict) -> dict:
        """Phase 3: Final Output Generation."""
        print(f"\n{'─'*50}")
        print("PHASE 3: FINAL OUTPUT GENERATION")
        print(f"{'─'*50}")

        agent_outputs = self._build_legacy_agent_outputs()

        # Risk Agent
        risk_output = None
        if self.risk_agent:
            print(f"→ Generating risk assessment...")
            try:
                risk_output = self.risk_agent.analyze(entity=entity, agent_outputs=agent_outputs)
                overall = risk_output.get('metrics', {}).get('overall_risk', 'unknown')
                print(f"  Risk: {overall.upper()}")
            except Exception as e:
                print(f"  ⚠️  Risk agent failed: {e}")
                risk_output = {"status": "failed", "error": str(e)}

        # Hypotheses
        hypotheses_output = None
        if config.get('hypotheses') and self.hypotheses_runner:
            print(f"→ Generating hypotheses...")
            try:
                hypotheses_output = self.hypotheses_runner(entity, self.register)
                from reports.hypothesis import format_hypotheses
                print(format_hypotheses(hypotheses_output))
            except Exception as e:
                print(f"  ⚠️  Hypothesis generation failed: {e}")
                hypotheses_output = {"status": "failed", "error": str(e)}

        # Compile final results
        latest_critic = self.critic_history[-1] if self.critic_history else {}
        dash = latest_critic.get("dashboard", {})

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