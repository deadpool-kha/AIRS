"""
agents/risk.py

Risk Agent for AIRS.
Identifies downside risks and weaknesses from all agent outputs.
Pure Python/rules-based — no LLM required.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


class RiskAgent:
    """Analyzes downside risks from all agent outputs."""

    def analyze(self, entity: str, agent_outputs: dict) -> dict:
        """
        Run risk analysis from all available agent outputs.

        Args:
            entity: Company or asset name
            agent_outputs: Dict with quant, technical, business outputs

        Returns:
            Structured risk assessment dict
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info(f"Risk Agent starting analysis for: {entity}")

        risks = []
        warnings = []

        # --- Extract agent outputs ---
        quant = agent_outputs.get("quant", {}).get("metrics", {})
        technical = agent_outputs.get("technical", {}).get("metrics", {})
        business = agent_outputs.get("business", {})

        # --- QUANT RISKS ---
        if quant.get("risk_score", 0) > 0.5:
            risks.append({
                "category": "volatility",
                "severity": "high",
                "description": f"High risk score: {quant['risk_score']:.2f}",
                "source": "quant_agent"
            })
        elif quant.get("risk_score", 0) > 0.3:
            warnings.append({
                "category": "volatility",
                "severity": "medium",
                "description": f"Elevated risk score: {quant['risk_score']:.2f}",
                "source": "quant_agent"
            })

        if quant.get("drawdown", {}).get("max_drawdown", 0) > 0.15:
            risks.append({
                "category": "drawdown",
                "severity": "high",
                "description": f"Significant drawdown: {quant['drawdown']['max_drawdown']:.1%}",
                "source": "quant_agent"
            })

        if quant.get("volatility", 0) > 0.4:
            risks.append({
                "category": "volatility",
                "severity": "high",
                "description": f"High volatility: {quant['volatility']:.1%}",
                "source": "quant_agent"
            })

        if quant.get("trend") in ["downtrend", "weak_downtrend"]:
            risks.append({
                "category": "momentum",
                "severity": "high",
                "description": f"Negative price trend: {quant['trend']}",
                "source": "quant_agent"
            })

        # --- TECHNICAL RISKS ---
        if technical.get("days_since_commit", 0) > 30:
            risks.append({
                "category": "development",
                "severity": "high",
                "description": f"Stale development: {technical['days_since_commit']} days since last commit",
                "source": "technical_agent"
            })
        elif technical.get("days_since_commit", 0) > 14:
            warnings.append({
                "category": "development",
                "severity": "medium",
                "description": f"Slowing development: {technical['days_since_commit']} days since last commit",
                "source": "technical_agent"
            })

        if technical.get("health_score", 1.0) < 0.4:
            risks.append({
                "category": "ecosystem",
                "severity": "high",
                "description": f"Unhealthy ecosystem: health score {technical['health_score']:.2f}",
                "source": "technical_agent"
            })
        elif technical.get("health_score", 1.0) < 0.6:
            warnings.append({
                "category": "ecosystem",
                "severity": "medium",
                "description": f"Declining ecosystem health: {technical['health_score']:.2f}",
                "source": "technical_agent"
            })

        if technical.get("contributor_count", 999) < 5:
            risks.append({
                "category": "ecosystem",
                "severity": "medium",
                "description": f"Few contributors: {technical['contributor_count']}",
                "source": "technical_agent"
            })

        # --- BUSINESS RISKS ---
        if business.get("status") == "partial":
            warnings.append({
                "category": "information",
                "severity": "medium",
                "description": "Limited business data available",
                "source": "business_agent"
            })

        # Business agent negative signals
        biz_signals = business.get("signals", [])
        for signal in biz_signals:
            if signal.get("type") == "negative":
                risks.append({
                    "category": signal.get("category", "business"),
                    "severity": "high",
                    "description": signal.get("description", "Negative business signal"),
                    "source": "business_agent"
                })

        # Business agent extracted risks
        biz_risks = business.get("risks", [])
        for risk in biz_risks:
            risks.append({
                "category": "business",
                "severity": "medium",
                "description": risk,
                "source": "business_agent"
            })

        # --- CROSS-AGENT RISKS ---
        # Contradiction: strong quant + weak technical
        if quant.get("trend") == "strong_uptrend" and technical.get("health_score", 1.0) < 0.5:
            risks.append({
                "category": "contradiction",
                "severity": "high",
                "description": "Price trending up but ecosystem deteriorating — potential divergence",
                "source": "cross_agent"
            })

        # Concentration: everything positive (no diversification of signals)
        all_positive = (
            quant.get("trend") == "strong_uptrend" and
            technical.get("health_score", 0) > 0.7 and
            len([s for s in biz_signals if s.get("type") == "negative"]) == 0
        )
        if all_positive and len(risks) == 0:
            warnings.append({
                "category": "blind_spot",
                "severity": "medium",
                "description": "All signals positive — potential blind spots or confirmation bias",
                "source": "cross_agent"
            })

        # --- CALCULATE CONFIDENCE ---
        confidence = self._calculate_confidence(risks, warnings, agent_outputs)

        # --- DETERMINE STATUS ---
        if len(risks) == 0 and len(warnings) == 0:
            status = "complete"
            overall_risk = "low"
        elif len(risks) > 0:
            status = "complete"
            overall_risk = "high"
        else:
            status = "complete"
            overall_risk = "medium"

        logger.info(f"Risk Agent complete for {entity} — {len(risks)} risks, {len(warnings)} warnings")

        return {
            "agent": "risk",
            "entity": entity,
            "timestamp": timestamp,
            "metrics": {
                "risk_count": len(risks),
                "warning_count": len(warnings),
                "overall_risk": overall_risk,
                "high_severity_count": len([r for r in risks if r["severity"] == "high"]),
                "medium_severity_count": len([r for r in risks if r["severity"] == "medium"] + warnings),
            },
            "risks": risks,
            "warnings": warnings,
            "confidence": confidence,
            "status": status,
            "sources": list({r["source"] for r in risks + warnings}) or ["rule_based"],
        }

    def _calculate_confidence(self, risks: list, warnings: list, agent_outputs: dict) -> float:
        """Calculate confidence in risk assessment."""
        # Component 1: Data availability (40%)
        available_agents = sum([
            1 for k in ["quant", "technical", "business"]
            if agent_outputs.get(k, {}).get("status") in ["complete", "partial"]
        ])
        data_score = min(available_agents / 3, 1.0) * 0.4

        # Component 2: Risk identification coverage (30%)
        # More risks found = higher confidence we didn't miss anything
        total_findings = len(risks) + len(warnings)
        coverage_score = min(total_findings / 5, 1.0) * 0.3

        # Component 3: Severity diversity (20%)
        # Mix of high/medium/low = thorough analysis
        severities = {r["severity"] for r in risks + warnings}
        diversity_score = min(len(severities) / 2, 1.0) * 0.2

        # Component 4: Cross-agent validation (10%)
        sources = {r["source"] for r in risks + warnings}
        cross_score = min(len(sources) / 2, 1.0) * 0.1

        total = data_score + coverage_score + diversity_score + cross_score
        return round(min(total, 1.0), 4)