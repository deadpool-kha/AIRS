"""
controller/loop.py

Loop Controller for AIRS (Issue #9).
- Orchestrates agent execution, critique, and iteration
- Handles missing agents gracefully (no crash if quant/technical/repo absent)
- Enforces max 3 iterations
- Persists loop state to SQLite
"""

import json
import sqlite3
from typing import Dict, Callable
from datetime import datetime, timezone

from data.db import DB_PATH
from agents.critic import CriticAgent
from agents.risk import RiskAgent


class LoopController:
    MAX_ITERATIONS = 3

    def __init__(self, ollama_client=None):
        self.db_path = str(DB_PATH)
        self.critic = CriticAgent(ollama_client=ollama_client)
        self.risk_agent = RiskAgent()
        self.iteration = 0
        self.agent_outputs_history = []
        self.critic_history = []
        self._ensure_table()

    def _ensure_table(self):
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
                    should_iterate_history TEXT
                )
            """)
            conn.commit()

    def _persist(self, entity: str, status: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM loop_states WHERE entity = ? AND status = 'running' ORDER BY id DESC LIMIT 1",
                (entity,)
            )
            row = cursor.fetchone()
            should_iter = json.dumps([c.get('should_iterate', False) for c in self.critic_history])
            summary = self._summarize_critique()
            now = datetime.now(timezone.utc).isoformat()

            if row:
                conn.execute(
                    """UPDATE loop_states 
                       SET completed_at = ?, final_iteration = ?, status = ?, critique_summary = ?, should_iterate_history = ?
                       WHERE id = ?""",
                    (now, self.iteration, status, summary, should_iter, row[0])
                )
            else:
                conn.execute(
                    """INSERT INTO loop_states (entity, status, final_iteration, critique_summary, should_iterate_history)
                       VALUES (?, ?, ?, ?, ?)""",
                    (entity, status, self.iteration, summary, should_iter)
                )
            conn.commit()

    def _summarize_critique(self) -> str:
        if not self.critic_history:
            return ""
        latest = self.critic_history[-1]
        return f"{latest['overall_quality']}, {latest['metrics']['gaps_count']} gaps, iterate={latest['should_iterate']}"

    def run(self, entity: str, agent_runners: Dict[str, Callable], config: dict, refinement_config: dict = None) -> dict:
        """
        Main orchestration loop.

        agent_runners: dict of agent_name -> callable returning result dict
        config: {'hypotheses': bool, 'show_sources': bool, ...}
        """
        self._persist(entity, 'running')
        final_outputs = {}

        try:
            while self.iteration < self.MAX_ITERATIONS:
                self.iteration += 1
                print(f"\n{'='*60}")
                print(f"LOOP ITERATION {self.iteration}/{self.MAX_ITERATIONS}")
                print(f"{'='*60}")

                # Phase 1: Execute available agents
                agent_outputs = {}
                for name, runner in agent_runners.items():
                    print(f"\n→ Running {name}...")
                    try:
                        result = runner()
                        agent_outputs[name] = result
                        print(f"  {name}: {result.get('status', 'unknown')}")
                    except Exception as e:
                        print(f"  ⚠️  {name} crashed: {e}")
                        agent_outputs[name] = {
                            "agent": name,
                            "status": "failed",
                            "error": str(e),
                            "confidence": 0.0,
                        }

                # Phase 2: Risk Agent (runs on whatever we have)
                has_any = any(
                    v.get('status') in ('complete', 'partial')
                    for v in agent_outputs.values()
                )
                if has_any:
                    try:
                        risk_result = self.risk_agent.analyze(
                            entity=entity, agent_outputs=agent_outputs
                        )
                        agent_outputs["risk"] = risk_result
                        print(f"  risk: {risk_result.get('status', 'unknown')}")
                    except Exception as e:
                        print(f"  ⚠️  risk crashed: {e}")
                        agent_outputs["risk"] = {
                            "agent": "risk",
                            "status": "failed",
                            "error": str(e),
                            "confidence": 0.0,
                        }
                else:
                    agent_outputs["risk"] = {
                        "agent": "risk",
                        "status": "skipped",
                        "error": "No agent outputs available for risk analysis",
                        "confidence": 0.0,
                    }

                self.agent_outputs_history.append(agent_outputs)
                final_outputs = agent_outputs

                # Phase 3: Critic
                print(f"\n→ Running critic...")
                critic_result = self.critic.evaluate_with_llm(
                    entity, agent_outputs, self.iteration
                )
                self.critic_history.append(critic_result)
                agent_outputs["critic"] = critic_result
                self._display_critic(critic_result)

                    # Phase 4: Iterate?
                                # Phase 4: Iterate?
                if not critic_result.get('should_iterate', False):
                    print(f"\n✅ Critic satisfied. Halting at iteration {self.iteration}.")
                    break

                if self.iteration >= self.MAX_ITERATIONS:
                    print(f"\n⛔ Max iterations ({self.MAX_ITERATIONS}) reached. Halting.")
                    break

                # Phase 5: Refine plan
                self._refine_plan(critic_result, refinement_config or {})
                
            # Phase 6: Hypotheses
            if config.get('hypotheses'):
                print(f"\n→ Generating hypotheses...")
                try:
                    from reports.hypothesis import generate_hypotheses, format_hypotheses
                    hypotheses = generate_hypotheses(entity, final_outputs)
                    final_outputs["hypotheses"] = hypotheses
                    print(format_hypotheses(hypotheses))
                except Exception as e:
                    print(f"  ⚠️  Hypothesis generation failed: {e}")

            self._persist(entity, 'completed')
            return final_outputs

        except Exception:
            self._persist(entity, 'failed')
            raise

    def _display_critic(self, result: dict):
        print(f"\n{'='*50}")
        print(f"CRITIC EVALUATION (Iteration {result['iteration']})")
        print(f"{'='*50}")
        print(f"Quality: {result['overall_quality'].upper()}")
        print(f"Score: {result['metrics']['quality_score']}")
        print(f"Gaps: {result['metrics']['gaps_count']}")
        print(f"Iterate: {result['should_iterate']}")
        if result.get('gaps'):
            for gap in result['gaps']:
                print(f"  - {gap}")
        print(f"{'='*50}")

    def _refine_plan(self, critic_result: dict, refinement_config: dict):
        gaps = critic_result.get('gaps', [])
        print(f"\n🔁 Refining plan for iteration {self.iteration + 1}...")
        if not gaps:
            print("   No gaps to address.")
            return

        for gap in gaps:
            if gap in ('quant_incomplete', 'quant_low_confidence'):
                current = refinement_config.get('quant_period', '3mo')
                if current == '3mo':
                    refinement_config['quant_period'] = '6mo'
                    print("   → Extending quant data period to 6mo")
                elif current == '6mo':
                    refinement_config['quant_period'] = '1y'
                    print("   → Extending quant data period to 1y")
                else:
                    print("   → Quant period already at maximum (1y)")
                    
            elif gap in ('business_insufficient_news', 'business_failed'):
                if not refinement_config.get('business_broad_search'):
                    refinement_config['business_broad_search'] = True
                    print("   → Switching business search to broader terms (no ticker filter)")
                else:
                    print("   → Business search already at broadest")
                    
            elif gap == 'technical_failed':
                print("   → Technical repo failed — no alternative configured")
                
            elif gap == 'high_risk_not_mitigated':
                print("   → High risk flagged — re-evaluating with expanded context")
                
            elif gap == 'insufficient_dimensions':
                print("   → Attempting broader coverage")
                
            else:
                print(f"   → Gap '{gap}' noted for manual review")