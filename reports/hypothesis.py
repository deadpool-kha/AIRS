"""
reports/hypothesis.py
Issue #9b+: Evidence-Driven Loop Evolution — Hypothesis Redesign

Generates bull, bear, and base case hypotheses from the Evidence Register.

Key changes:
- Directional bias (bull vs bear) is computed from evidence weights, not arbitrary points
- Uncertainty is a separate dimension — reflects evidence quality, conflict, and coverage
- Base case captures neutral/moderate signals, not "leftover" probability mass
- No artificial probability floors — if a case has no evidence, it says so honestly
- Every claim is traceable to source, raw value, and strength
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from core.evidence import EvidenceRegister


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EvidenceClaim:
    """A single piece of evidence supporting or contradicting a hypothesis."""
    description: str
    source: str          # "quant", "business", "technical"
    direction: str       # "bullish", "bearish", "neutral"
    strength: float      # 0.0 to 1.0
    raw_value: Any = None

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "source": self.source,
            "direction": self.direction,
            "strength": round(self.strength, 4),
            "raw_value": str(self.raw_value) if self.raw_value is not None else None,
        }


@dataclass
class HypothesisCase:
    """Represents a single investment hypothesis case."""
    name: str
    thesis: str
    claims: List[EvidenceClaim] = field(default_factory=list)

    @property
    def total_strength(self) -> float:
        return sum(c.strength for c in self.claims)

    @property
    def evidence_count(self) -> int:
        return len(self.claims)

    def to_dict(self, legacy_probability: float = 0.0) -> dict:
        """Return dict with both new claims and legacy-compatible keys."""
        return {
            "name": self.name,
            "thesis": self.thesis,
            "probability": round(legacy_probability, 4),   # legacy
            "supporting_evidence": [c.description for c in self.claims],  # legacy
            "contradicting_evidence": [],  # legacy — kept empty, conflicts live in other cases
            "confidence": round(self.total_strength, 4),
            "claims": [c.to_dict() for c in self.claims],
            "total_strength": round(self.total_strength, 4),
            "evidence_count": self.evidence_count,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# EVIDENCE ASSESSMENT — Convert raw register data into directional claims
# ═══════════════════════════════════════════════════════════════════════════════

def _assess_evidence(entity: str, register: EvidenceRegister) -> Dict[str, List[EvidenceClaim]]:
    """
    Read the Evidence Register and convert raw metrics into directional claims.

    Each claim has:
    - description: human-readable
    - source: which dimension produced it
    - direction: bullish, bearish, or neutral
    - strength: 0.0-1.0 based on magnitude and reliability
    - raw_value: the actual number/string from the register
    """
    claims: Dict[str, List[EvidenceClaim]] = {"bullish": [], "bearish": [], "neutral": []}

    # Only read dimensions that ACTUALLY exist in the register
    has_quant = register.has("trend") or register.has("risk_score") or register.has("returns")
    has_business = register.has("business_context")
    has_technical = register.has("technical_context")

    # ── QUANT ──
    if has_quant:
        if register.has("trend"):
            trend = register.get("trend")
            if trend == "strong_uptrend":
                claims["bullish"].append(EvidenceClaim(
                    "Strong price momentum and uptrend", "quant", "bullish", 0.85, trend))
            elif trend == "uptrend":
                claims["bullish"].append(EvidenceClaim(
                    "Price in uptrend", "quant", "bullish", 0.60, trend))
            elif trend == "strong_downtrend":
                claims["bearish"].append(EvidenceClaim(
                    "Strong price downtrend", "quant", "bearish", 0.85, trend))
            elif trend == "downtrend":
                claims["bearish"].append(EvidenceClaim(
                    "Price in downtrend", "quant", "bearish", 0.60, trend))

        if register.has("returns"):
            returns = register.get("returns")
            if isinstance(returns, dict):
                monthly = returns.get("monthly")
                if isinstance(monthly, (int, float)):
                    if monthly > 10:
                        claims["bullish"].append(EvidenceClaim(
                            f"Strong monthly return: {monthly}%", "quant", "bullish", 0.70, monthly))
                    elif monthly > 5:
                        claims["bullish"].append(EvidenceClaim(
                            f"Solid monthly return: {monthly}%", "quant", "bullish", 0.50, monthly))
                    elif monthly < -10:
                        claims["bearish"].append(EvidenceClaim(
                            f"Severe monthly decline: {monthly}%", "quant", "bearish", 0.70, monthly))
                    elif monthly < -5:
                        claims["bearish"].append(EvidenceClaim(
                            f"Monthly decline: {monthly}%", "quant", "bearish", 0.50, monthly))

        if register.has("momentum"):
            momentum = register.get("momentum")
            if isinstance(momentum, dict):
                m20 = momentum.get("20d")
                if isinstance(m20, (int, float)):
                    if m20 > 0.15:
                        claims["bullish"].append(EvidenceClaim(
                            f"Strong 20-day momentum: {m20:.1%}", "quant", "bullish", 0.65, m20))
                    elif m20 > 0.05:
                        claims["bullish"].append(EvidenceClaim(
                            f"Positive 20-day momentum: {m20:.1%}", "quant", "bullish", 0.40, m20))
                    elif m20 < -0.15:
                        claims["bearish"].append(EvidenceClaim(
                            f"Strong negative 20-day momentum: {m20:.1%}", "quant", "bearish", 0.65, m20))
                    elif m20 < -0.05:
                        claims["bearish"].append(EvidenceClaim(
                            f"Negative 20-day momentum: {m20:.1%}", "quant", "bearish", 0.40, m20))

        if register.has("macd"):
            macd = register.get("macd")
            if isinstance(macd, dict):
                signal = macd.get("signal", "")
                if "bullish_crossover" in signal:
                    claims["bullish"].append(EvidenceClaim(
                        f"MACD bullish crossover — momentum turning positive", "quant", "bullish", 0.70, signal))
                elif "bullish" in signal:
                    claims["bullish"].append(EvidenceClaim(
                        f"MACD {signal} — positive momentum", "quant", "bullish", 0.50, signal))
                elif "bearish_crossover" in signal:
                    claims["bearish"].append(EvidenceClaim(
                        f"MACD bearish crossover — momentum turning negative", "quant", "bearish", 0.70, signal))
                elif "bearish" in signal:
                    claims["bearish"].append(EvidenceClaim(
                        f"MACD {signal} — negative momentum", "quant", "bearish", 0.50, signal))

        if register.has("rsi"):
            rsi = register.get("rsi")
            if isinstance(rsi, (int, float)):
                if rsi < 25:
                    claims["bullish"].append(EvidenceClaim(
                        f"RSI {rsi:.1f} — deeply oversold, mean reversion potential", "quant", "bullish", 0.60, rsi))
                elif rsi < 35:
                    claims["bullish"].append(EvidenceClaim(
                        f"RSI {rsi:.1f} — oversold, potential mean reversion", "quant", "bullish", 0.45, rsi))
                elif rsi > 75:
                    claims["bearish"].append(EvidenceClaim(
                        f"RSI {rsi:.1f} — deeply overbought, pullback risk", "quant", "bearish", 0.60, rsi))
                elif rsi > 65:
                    claims["bearish"].append(EvidenceClaim(
                        f"RSI {rsi:.1f} — overbought, potential pullback", "quant", "bearish", 0.45, rsi))
                elif 40 <= rsi <= 60:
                    claims["neutral"].append(EvidenceClaim(
                        f"RSI {rsi:.1f} in neutral zone — no clear directional bias", "quant", "neutral", 0.30, rsi))

        if register.has("beta"):
            beta = register.get("beta")
            if isinstance(beta, (int, float)):
                if 0.5 < beta < 1.0:
                    claims["bullish"].append(EvidenceClaim(
                        f"Low beta ({beta:.2f}) — defensive growth profile", "quant", "bullish", 0.35, beta))
                elif beta > 1.5:
                    claims["bearish"].append(EvidenceClaim(
                        f"High beta ({beta:.2f}) — elevated systematic risk", "quant", "bearish", 0.45, beta))

        if register.has("risk_score"):
            rs = register.get("risk_score")
            if isinstance(rs, (int, float)):
                if rs > 0.6:
                    claims["bearish"].append(EvidenceClaim(
                        f"High risk score: {rs:.2f}", "quant", "bearish", 0.75, rs))
                elif rs > 0.4:
                    claims["bearish"].append(EvidenceClaim(
                        f"Elevated risk score: {rs:.2f}", "quant", "bearish", 0.45, rs))
                elif 0.2 < rs < 0.4:
                    claims["neutral"].append(EvidenceClaim(
                        f"Moderate risk profile: {rs:.2f}", "quant", "neutral", 0.35, rs))

        if register.has("drawdown"):
            dd = register.get("drawdown")
            if isinstance(dd, dict):
                mdd = dd.get("max_drawdown", 0)
                if isinstance(mdd, (int, float)) and mdd > 0.20:
                    claims["bearish"].append(EvidenceClaim(
                        f"Severe drawdown: {mdd:.1%}", "quant", "bearish", 0.70, mdd))
                elif isinstance(mdd, (int, float)) and mdd > 0.10:
                    claims["bearish"].append(EvidenceClaim(
                        f"Significant drawdown: {mdd:.1%}", "quant", "bearish", 0.50, mdd))

        if register.has("volatility_regime"):
            vr = register.get("volatility_regime")
            if vr in ("extreme",):
                claims["bearish"].append(EvidenceClaim(
                    f"Extreme volatility regime", "quant", "bearish", 0.60, vr))
            elif vr in ("elevated",):
                claims["bearish"].append(EvidenceClaim(
                    f"Elevated volatility regime", "quant", "bearish", 0.45, vr))
            elif vr == "normal":
                claims["neutral"].append(EvidenceClaim(
                    "Normal volatility regime", "quant", "neutral", 0.25, vr))

        if register.has("volatility"):
            vol = register.get("volatility")
            if isinstance(vol, (int, float)) and vol < 0.25:
                claims["neutral"].append(EvidenceClaim(
                    f"Stable volatility: {vol:.1%}", "quant", "neutral", 0.30, vol))

    # ── BUSINESS ──
    if has_business:
        business = register.get("business_context")
        if isinstance(business, dict):
            metrics = business.get("metrics", {})
            pos = metrics.get("positive_signals", 0)
            neg = metrics.get("negative_signals", 0)

            if pos > 3:
                claims["bullish"].append(EvidenceClaim(
                    f"{pos} positive business signals", "business", "bullish", min(0.30 + pos * 0.05, 0.80), pos))
            elif pos > 0:
                claims["bullish"].append(EvidenceClaim(
                    f"{pos} positive business signal(s)", "business", "bullish", 0.20 + pos * 0.05, pos))

            if neg > 2:
                claims["bearish"].append(EvidenceClaim(
                    f"{neg} negative business signals", "business", "bearish", min(0.30 + neg * 0.05, 0.80), neg))
            elif neg > 0:
                claims["bearish"].append(EvidenceClaim(
                    f"{neg} negative business signal(s)", "business", "bearish", 0.20 + neg * 0.05, neg))

            risks = business.get("risks", [])
            if risks:
                claims["bearish"].append(EvidenceClaim(
                    f"{len(risks)} business risks identified", "business", "bearish",
                    min(0.25 + len(risks) * 0.08, 0.60), len(risks)))

            catalysts = business.get("catalysts", [])
            if catalysts:
                claims["bullish"].append(EvidenceClaim(
                    f"{len(catalysts)} catalyst(s) identified", "business", "bullish",
                    min(0.25 + len(catalysts) * 0.08, 0.60), len(catalysts)))

    # ── TECHNICAL ──
    if has_technical:
        technical = register.get("technical_context")
        if isinstance(technical, dict):
            t_metrics = technical.get("metrics", {})
            health = t_metrics.get("health_score", 0)
            if isinstance(health, (int, float)):
                if health > 0.7:
                    claims["bullish"].append(EvidenceClaim(
                        f"Healthy developer ecosystem (health: {health:.2f})", "technical", "bullish", 0.55, health))
                elif health < 0.4:
                    claims["bearish"].append(EvidenceClaim(
                        f"Unhealthy developer ecosystem (health: {health:.2f})", "technical", "bearish", 0.55, health))
                else:
                    claims["neutral"].append(EvidenceClaim(
                        f"Moderate ecosystem health (health: {health:.2f})", "technical", "neutral", 0.30, health))

            freq = t_metrics.get("commit_frequency", 0)
            if isinstance(freq, (int, float)) and freq > 10:
                claims["bullish"].append(EvidenceClaim(
                    f"High development activity: {freq}/week", "technical", "bullish", 0.45, freq))

            days = t_metrics.get("days_since_commit", 999)
            if isinstance(days, (int, float)) and days > 30:
                claims["bearish"].append(EvidenceClaim(
                    f"Stale development: {days} days since last commit", "technical", "bearish", 0.50, days))
            elif isinstance(days, (int, float)) and days > 14:
                claims["neutral"].append(EvidenceClaim(
                    f"Slowing development: {days} days since last commit", "technical", "neutral", 0.25, days))

    return claims


# ═══════════════════════════════════════════════════════════════════════════════
# COMPUTATION — Directional bias and uncertainty
# ═══════════════════════════════════════════════════════════════════════════════

def _compute_directional_bias(claims: Dict[str, List[EvidenceClaim]]) -> Dict[str, Any]:
    """Compute directional bias from evidence claims."""
    bull_s = sum(c.strength for c in claims["bullish"])
    bear_s = sum(c.strength for c in claims["bearish"])

    return {
        "bull_strength": round(bull_s, 4),
        "bear_strength": round(bear_s, 4),
        "directional_score": round(bull_s - bear_s, 4),
        "net": "bullish" if bull_s - bear_s > 0.15 else "bearish" if bear_s - bull_s > 0.15 else "neutral",
        "bull_evidence_count": len(claims["bullish"]),
        "bear_evidence_count": len(claims["bearish"]),
    }


def _compute_uncertainty(
    claims: Dict[str, List[EvidenceClaim]], register: EvidenceRegister
) -> Dict[str, Any]:
    """
    Uncertainty measures how confident we are in the directional call.
    It is NOT leftover probability — it's epistemic humility.
    """
    bull = claims["bullish"]
    bear = claims["bearish"]
    neutral = claims["neutral"]
    total = len(bull) + len(bear) + len(neutral)

    if total == 0:
        return {"score": 1.0, "level": "Extreme", "reason": "No evidence available", "factors": {}}

    # Scarcity: few signals = high uncertainty
    scarcity = max(0.0, 0.35 - (total * 0.04))

    # Conflict: equal bull/bear strength = high uncertainty
    bull_s = sum(c.strength for c in bull)
    bear_s = sum(c.strength for c in bear)
    total_s = bull_s + bear_s

    if total_s > 0:
        ratio = min(bull_s, bear_s) / max(bull_s, bear_s) if max(bull_s, bear_s) > 0 else 0
        conflict = ratio * 0.40
    else:
        conflict = 0.0

    # Coverage: missing dimensions add uncertainty
    dims_present = 0
    dims_possible = 0
    if register.has("trend") or register.has("risk_score"):
        dims_present += 1
    dims_possible += 1
    if register.has("business_context"):
        dims_present += 1
    dims_possible += 1
    if register.has("technical_context"):
        dims_present += 1
    dims_possible += 1

    coverage = (1.0 - (dims_present / dims_possible)) * 0.25 if dims_possible > 0 else 0.25

    raw = scarcity + conflict + coverage
    score = min(raw, 1.0)

    if score < 0.20:
        level = "Low"
    elif score < 0.40:
        level = "Moderate"
    elif score < 0.60:
        level = "Elevated"
    elif score < 0.80:
        level = "High"
    else:
        level = "Extreme"

    return {
        "score": round(score, 4),
        "level": level,
        "reason": f"Scarcity={scarcity:.2f}, Conflict={conflict:.2f}, Coverage={coverage:.2f}",
        "factors": {"scarcity": round(scarcity, 4), "conflict": round(conflict, 4), "coverage": round(coverage, 4)},
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PRIMARY ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def generate_from_register(entity: str, evidence_register: EvidenceRegister) -> dict:
    """
    Generate hypotheses directly from the Evidence Register.

    Returns:
        Dict with:
        - bull/bear/base cases (with claims)
        - directional_bias (strength-based, not probability)
        - uncertainty (separate score)
        - legacy probability keys for backward compatibility
    """
    bull = HypothesisCase("bull", f"{entity} is undervalued with upside potential")
    bear = HypothesisCase("bear", f"{entity} is overvalued or faces significant risks")
    base = HypothesisCase("base", f"{entity} is fairly valued with moderate growth")

    claims = _assess_evidence(entity, evidence_register)

    bull.claims = claims["bullish"]
    bear.claims = claims["bearish"]
    base.claims = claims["neutral"]

    bias = _compute_directional_bias(claims)
    uncertainty = _compute_uncertainty(claims, evidence_register)

    dimensions_used = []
    if evidence_register.has("trend") or evidence_register.has("risk_score"):
        dimensions_used.append("quant")
    if evidence_register.has("business_context"):
        dimensions_used.append("business")
    if evidence_register.has("technical_context"):
        dimensions_used.append("technical")

    # Legacy probabilities for backward compatibility
    bull_s = bias["bull_strength"]
    bear_s = bias["bear_strength"]
    total_s = bull_s + bear_s

    if total_s > 0:
        bull_prob = bull_s / total_s
        bear_prob = bear_s / total_s
    else:
        bull_prob = bear_prob = 0.0

    # Normalize to 100% for legacy display
    if total_s > 0:
        total_p = bull_prob + bear_prob
        bull_prob = bull_prob / total_p
        bear_prob = bear_prob / total_p

    return {
        # ── NEW ARCHITECTURE ──
        "bull": bull.to_dict(legacy_probability=bull_prob),
        "bear": bear.to_dict(legacy_probability=bear_prob),
        "base": base.to_dict(legacy_probability=0.0),
        "directional_bias": bias,
        "uncertainty": uncertainty,

        # ── METADATA ──
        "entity": entity,
        "evidence_based": True,
        "evidence_count": len(evidence_register),
        "dimensions_used": dimensions_used,

        # ── LEGACY COMPATIBILITY ──
        "_legacy_probabilities": {
            "bull": round(bull_prob, 4),
            "bear": round(bear_prob, 4),
            "base": 0.0,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATTING — New dashboard style
# ═══════════════════════════════════════════════════════════════════════════════

def format_hypotheses(hypotheses: dict) -> str:
    """Format hypotheses for display — DASHBOARD STYLE."""
    bias = hypotheses.get("directional_bias", {})
    uncertainty = hypotheses.get("uncertainty", {})

    net = bias.get("net", "unknown")
    bull_s = bias.get("bull_strength", 0)
    bear_s = bias.get("bear_strength", 0)
    bull_n = bias.get("bull_evidence_count", 0)
    bear_n = bias.get("bear_evidence_count", 0)

    lines = [
        f"\n{'='*60}",
        f"INVESTMENT HYPOTHESES: {hypotheses['entity']}",
        f"{'='*60}",
        "",
        f"DIRECTIONAL BIAS: {net.upper()}",
        f"  Bullish strength: {bull_s:.2f}  ({bull_n} claims)",
        f"  Bearish strength: {bear_s:.2f}  ({bear_n} claims)",
        f"  Net score: {bias.get('directional_score', 0):+.2f}",
        "",
        f"UNCERTAINTY: {uncertainty.get('level', 'Unknown')} ({uncertainty.get('score', 0):.0%})",
        f"  {uncertainty.get('reason', '')}",
        f"{'='*60}",
        "",
        f"BULL CASE — {bull_n} evidence items (strength: {bull_s:.2f})",
        f"  Thesis: {hypotheses['bull']['thesis']}",
    ]

    for claim in hypotheses["bull"]["claims"]:
        icon = "++" if claim["strength"] > 0.6 else "+" if claim["strength"] > 0.4 else "+"
        lines.append(f"    {icon} [{claim['source']}] {claim['description']}")

    if not hypotheses["bull"]["claims"]:
        lines.append("    (No bullish evidence)")

    lines.extend([
        "",
        f"BEAR CASE — {bear_n} evidence items (strength: {bear_s:.2f})",
        f"  Thesis: {hypotheses['bear']['thesis']}",
    ])

    for claim in hypotheses["bear"]["claims"]:
        icon = "--" if claim["strength"] > 0.6 else "-" if claim["strength"] > 0.4 else "-"
        lines.append(f"    {icon} [{claim['source']}] {claim['description']}")

    if not hypotheses["bear"]["claims"]:
        lines.append("    (No bearish evidence)")

    lines.extend([
        "",
        f"BASE / NEUTRAL — {len(hypotheses['base']['claims'])} evidence items",
        f"  Thesis: {hypotheses['base']['thesis']}",
    ])

    for claim in hypotheses["base"]["claims"]:
        lines.append(f"    ~ [{claim['source']}] {claim['description']}")

    if not hypotheses["base"]["claims"]:
        lines.append("    (No neutral evidence)")

    lines.extend([
        "",
        f"Generated from {hypotheses.get('evidence_count', '?')} evidence items",
        f"Dimensions used: {', '.join(hypotheses.get('dimensions_used', [])) if hypotheses.get('dimensions_used') else 'None'}",
        f"{'='*60}",
    ])

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY: Agent-Output-Based Generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_hypotheses(entity: str, agent_outputs: dict) -> dict:
    """Legacy method. Preserved for direct use outside the evidence-driven loop."""
    bull = HypothesisCase("bull", f"{entity} is undervalued with upside potential")
    bear = HypothesisCase("bear", f"{entity} is overvalued or faces significant risks")
    base = HypothesisCase("base", f"{entity} is fairly valued with moderate growth")

    quant_status = agent_outputs.get("quant", {}).get("status", "failed")
    technical_status = agent_outputs.get("technical", {}).get("status", "failed")
    business_status = agent_outputs.get("business", {}).get("status", "failed")

    quant = agent_outputs.get("quant", {}).get("metrics", {}) if quant_status == "complete" else {}
    technical = agent_outputs.get("technical", {}).get("metrics", {}) if technical_status in ["complete", "partial"] else {}
    business = agent_outputs.get("business", {}) if business_status in ["complete", "partial"] else {}
    risk = agent_outputs.get("risk", {}).get("risks", [])

    # Populate with legacy point logic (kept for compatibility)
    if quant.get("trend") == "strong_uptrend":
        bull.claims.append(EvidenceClaim("Strong price momentum and uptrend", "quant", "bullish", 0.15, None))
    if quant.get("returns", {}).get("monthly", 0) > 5:
        bull.claims.append(EvidenceClaim(f"Strong monthly return: {quant['returns']['monthly']}%", "quant", "bullish", 0.10, None))
    if technical.get("health_score", 0) > 0.7:
        bull.claims.append(EvidenceClaim("Healthy developer ecosystem", "technical", "bullish", 0.10, None))
    if technical.get("commit_frequency", 0) > 10:
        bull.claims.append(EvidenceClaim(f"High development activity: {technical['commit_frequency']}/week", "technical", "bullish", 0.10, None))

    if quant and quant.get("risk_score", 0) > 0.5:
        bear.claims.append(EvidenceClaim(f"High risk score: {quant['risk_score']}", "quant", "bearish", 0.15, None))
    if quant and quant.get("drawdown", {}).get("max_drawdown", 0) > 0.15:
        bear.claims.append(EvidenceClaim(f"Significant drawdown: {quant['drawdown']['max_drawdown']:.1%}", "quant", "bearish", 0.10, None))
    if technical and technical.get("days_since_commit", 999) > 30:
        bear.claims.append(EvidenceClaim("Stale development activity", "technical", "bearish", 0.10, None))
    if any(r.get("severity") == "high" for r in risk):
        bear.claims.append(EvidenceClaim("High-severity risks identified", "risk", "bearish", 0.15, None))

    risk_metrics = agent_outputs.get("risk", {}).get("metrics", {})
    risk_level = risk_metrics.get("overall_risk", "low")
    if risk_level == "high":
        bear.claims.append(EvidenceClaim("Risk Agent flagged HIGH overall risk", "risk", "bearish", 0.15, None))

    risk_list = agent_outputs.get("risk", {}).get("risks", [])
    for r in risk_list:
        bear.claims.append(EvidenceClaim(f"Risk: {r.get('description', 'Unknown risk')}", "risk", "bearish", 0.05, None))

    warning_list = agent_outputs.get("risk", {}).get("warnings", [])
    for w in warning_list:
        bear.claims.append(EvidenceClaim(f"Warning: {w.get('description', 'Unknown warning')}", "risk", "bearish", 0.03, None))

    if quant and 0.3 < quant.get("risk_score", 0) < 0.5:
        base.claims.append(EvidenceClaim("Moderate risk profile", "quant", "neutral", 0.15, None))
    if technical and 0.5 < technical.get("health_score", 0) < 0.8:
        base.claims.append(EvidenceClaim("Moderate ecosystem health", "technical", "neutral", 0.10, None))
    if quant and quant.get("volatility", 0) < 0.3:
        base.claims.append(EvidenceClaim("Stable volatility", "quant", "neutral", 0.10, None))

    bull_s = bull.total_strength
    bear_s = bear.total_strength
    base_s = base.total_strength
    total = bull_s + bear_s + base_s

    if total > 0:
        bull_p = bull_s / total
        bear_p = bear_s / total
        base_p = base_s / total
    else:
        bull_p = bear_p = base_p = 0.33

    return {
        "bull": bull.to_dict(legacy_probability=bull_p),
        "bear": bear.to_dict(legacy_probability=bear_p),
        "base": base.to_dict(legacy_probability=base_p),
        "entity": entity,
        "evidence_based": False,
    }