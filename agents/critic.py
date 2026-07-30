"""
agents/critic.py

Critic Agent for AIRS.
Evaluates research quality across all agents.
Identifies gaps, unsupported claims, and missing evidence.
Uses Ollama for reasoning but keeps findings structured.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from utils.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class CriticAgent:
    """Evaluates research quality and identifies gaps."""

    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.ollama = ollama_client or OllamaClient()

    def evaluate(self, entity: str, agent_outputs: dict, iteration: int = 1) -> dict:
        """
        Evaluate research quality from all agent outputs.

        Args:
            entity: Company or asset name
            agent_outputs: Dict with quant, technical, business, risk outputs
            iteration: Current loop iteration (1-3)

        Returns:
            Structured critique dict
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info(f"Critic Agent evaluating {entity} (iteration {iteration})")

        # Build quality assessment
        gaps = []
        recommendations = []
        warnings = []

        # --- Check each agent ---
        quant = agent_outputs.get("quant", {})
        technical = agent_outputs.get("technical", {})
        business = agent_outputs.get("business", {})
        risk = agent_outputs.get("risk", {})

           # QUANT CHECKS
        if quant.get("status") == "skipped":
            pass  # Intentionally skipped (no ticker provided)
        elif quant.get("status") != "complete":
            gaps.append("quant_incomplete")
            recommendations.append("Re-run Quant Agent with valid ticker")
        elif quant.get("confidence", 0) < 0.7:
            gaps.append("quant_low_confidence")
            recommendations.append("Expand data period or verify data source")

            # TECHNICAL CHECKS
        if technical.get("status") == "failed":
            gaps.append("technical_failed")
            recommendations.append("Check GitHub repo name or API rate limits")
        elif technical.get("status") == "skipped":
            pass  # Intentionally skipped (no --repo provided)
        elif technical.get("metrics", {}).get("health_score", 0) == 0:
            gaps.append("technical_no_data")
            recommendations.append("Verify repository exists and is public")

        # BUSINESS CHECKS
        if business.get("status") == "partial":
            gaps.append("business_insufficient_news")
            recommendations.append("Try alternative news sources or broader ticker")
        elif business.get("status") == "failed":
            gaps.append("business_failed")
            recommendations.append("Check Ollama is running")

        # RISK CHECKS
        if risk.get("status") != "complete":
            gaps.append("risk_not_evaluated")
            recommendations.append("Run Risk Agent after other agents")
        elif risk.get("metrics", {}).get("risk_count", 0) == 0:
            risk_warnings = risk.get("metrics", {}).get("warning_count", 0)
            if risk_warnings == 0:
                gaps.append("no_risks_identified")
                recommendations.append("Manual risk review recommended — blind spot possible")

        # CROSS-AGENT CHECKS
        # Contradiction: high confidence quant + high risk
        quant_conf = quant.get("confidence", 0)
        risk_level = risk.get("metrics", {}).get("overall_risk", "low")
        if quant_conf > 0.8 and risk_level == "high":
            gaps.append("confidence_risk_mismatch")
            recommendations.append("Reconcile high quant confidence with high risk rating")

        # NEW: High risk requires iteration to investigate
        if risk_level == "high" and iteration < 3:
            gaps.append("high_risk_not_mitigated")
            recommendations.append("High risk identified — expand risk analysis or verify mitigations")

        # NEW: Business signal bias check
        biz_signals = business.get("signals", [])
        negative_signals = [s for s in biz_signals if s.get("type") == "negative"]
        if len(biz_signals) > 2 and len(negative_signals) == 0:
            warnings.append("business_no_negative_signals")
            recommendations.append("Verify news sources — no negative coverage may indicate bias")

        # Missing dimensions
        available = sum([
            1 for k in ["quant", "technical", "business", "risk"]
            if agent_outputs.get(k, {}).get("status") in ["complete", "partial"]
        ])
        if available < 3:
            gaps.append("insufficient_dimensions")
            recommendations.append(f"Only {available}/4 analysis dimensions available")

        # --- Calculate quality ---
        total_checks = 8  # quant, technical, business, risk, cross, dimensions, etc.
        passed = total_checks - len(gaps)
        quality_score = round(passed / total_checks, 4)

        # Determine if we should iterate
        should_iterate = len(gaps) > 0 and iteration < 3

        # Overall quality label
        if quality_score >= 0.8 and len(gaps) == 0:
            overall = "complete"
        elif quality_score >= 0.5:
            overall = "partial"
        else:
            overall = "insufficient"

        logger.info(f"Critic complete: {overall}, {len(gaps)} gaps, iterate={should_iterate}")

        return {
            "agent": "critic",
            "entity": entity,
            "timestamp": timestamp,
            "iteration": iteration,
            "metrics": {
                "quality_score": quality_score,
                "gaps_count": len(gaps),
                "warnings_count": len(warnings),
                "recommendations_count": len(recommendations),
            },
            "overall_quality": overall,
            "gaps": gaps,
            "warnings": warnings,
            "recommendations": recommendations,
            "should_iterate": should_iterate,
            "status": "complete",
            "sources": ["rule_based", "cross_agent_validation"],
        }

    def evaluate_with_llm(self, entity: str, agent_outputs: dict, iteration: int = 1) -> dict:
        """
        Optional: Use Ollama for deeper qualitative critique.
        Falls back to rule-based if LLM unavailable.
        """
        # Start with rule-based
        base = self.evaluate(entity, agent_outputs, iteration)

        # Skip LLM if already complete or no gaps
        if base["overall_quality"] == "complete" or not base["should_iterate"]:
            return base

        # Build prompt for LLM
        summary = self._build_summary(agent_outputs)
        prompt = f"""You are a senior investment analyst reviewing research quality.

Research on: {entity}
Iteration: {iteration}/3

Current gaps found: {', '.join(base['gaps'])}

Agent summaries:
{summary}

Task: Suggest 1-2 specific, actionable improvements. Be concise (2 sentences max).

Improvements:"""

        try:
            response = self.ollama.generate(prompt, timeout=30)
            base["llm_suggestions"] = response.strip()
            base["sources"].append("ollama_reasoning")
        except Exception as e:
            logger.warning(f"LLM critique failed, using rule-based only: {e}")
            base["llm_suggestions"] = None

        return base

    def _build_summary(self, agent_outputs: dict) -> str:
        """Build a text summary of agent outputs for LLM prompt."""
        lines = []
        for agent_name, output in agent_outputs.items():
            status = output.get("status", "unknown")
            conf = output.get("confidence", 0)
            lines.append(f"- {agent_name}: status={status}, confidence={conf}")
        return "\n".join(lines)