"""
reports/hypothesis.py

Hypothesis Competition Engine.
Generates bull, bear, and base case hypotheses from agent outputs.
Each hypothesis gathers evidence and gets a probability score.
"""

from typing import Dict, List


class Hypothesis:
    """Represents a single investment hypothesis."""
    
    def __init__(self, name: str, thesis: str):
        self.name = name
        self.thesis = thesis
        self.supporting_evidence: List[str] = []
        self.contradicting_evidence: List[str] = []
        self.probability: float = 0.0
    
    def add_evidence(self, evidence: str, supports: bool = True):
        if supports:
            self.supporting_evidence.append(evidence)
        else:
            self.contradicting_evidence.append(evidence)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "thesis": self.thesis,
            "probability": round(self.probability, 4),
            "supporting_evidence": self.supporting_evidence,
            "contradicting_evidence": self.contradicting_evidence,
            "confidence": self._calculate_confidence()
        }
    
    def _calculate_confidence(self) -> float:
        """Confidence based on evidence quality."""
        total = len(self.supporting_evidence) + len(self.contradicting_evidence)
        if total == 0:
            return 0.0
        return round(len(self.supporting_evidence) / total, 4)


def generate_hypotheses(entity: str, agent_outputs: dict) -> dict:
    """
    Generates competing hypotheses from agent outputs.
    
    Args:
        entity: Company or asset name
        agent_outputs: Dict with quant, technical, business, risk outputs
    
    Returns:
        Dict with bull, bear, base cases
    """
    bull = Hypothesis("bull", f"{entity} is undervalued with upside potential")
    bear = Hypothesis("bear", f"{entity} is overvalued or faces significant risks")
    base = Hypothesis("base", f"{entity} is fairly valued with moderate growth")
    
    # Extract data from agents
    quant = agent_outputs.get("quant", {}).get("metrics", {})
    technical = agent_outputs.get("technical", {}).get("metrics", {})
    risk = agent_outputs.get("risk", {}).get("risks", [])
    
    # --- BULL CASE EVIDENCE ---
    if quant.get("trend") == "strong_uptrend":
        bull.add_evidence("Strong price momentum and uptrend")
        bull.probability += 0.15
    
    if quant.get("returns", {}).get("monthly", 0) > 5:
        bull.add_evidence(f"Strong monthly return: {quant['returns']['monthly']}%")
        bull.probability += 0.10
    
    if technical.get("health_score", 0) > 0.7:
        bull.add_evidence("Healthy developer ecosystem")
        bull.probability += 0.10
    
    if technical.get("commit_frequency", 0) > 10:
        bull.add_evidence(f"High development activity: {technical['commit_frequency']}/week")
        bull.probability += 0.10
    
    # --- BEAR CASE EVIDENCE ---
    if quant.get("risk_score", 0) > 0.5:
        bear.add_evidence(f"High risk score: {quant['risk_score']}")
        bear.probability += 0.15
    
    if quant.get("drawdown", {}).get("max_drawdown", 0) > 0.15:
        bear.add_evidence(f"Significant drawdown: {quant['drawdown']['max_drawdown']:.1%}")
        bear.probability += 0.10
    
    if technical.get("days_since_commit", 999) > 30:
        bear.add_evidence("Stale development activity")
        bear.probability += 0.10
    
    if any(r.get("severity") == "high" for r in risk):
        bear.add_evidence("High-severity risks identified")
        bear.probability += 0.15
    
    # --- BASE CASE (neutral/moderate signals) ---
    if 0.3 < quant.get("risk_score", 0) < 0.5:
        base.add_evidence("Moderate risk profile")
        base.probability += 0.15
    
    if 0.5 < technical.get("health_score", 0) < 0.8:
        base.add_evidence("Moderate ecosystem health")
        base.probability += 0.10
    
    if quant.get("volatility", 0) < 0.3:
        base.add_evidence("Stable volatility")
        base.probability += 0.10
    
    # Normalize probabilities to sum to 1.0
    total = bull.probability + bear.probability + base.probability
    
    if total > 0:
        bull.probability = round(bull.probability / total, 4)
        bear.probability = round(bear.probability / total, 4)
        base.probability = round(base.probability / total, 4)
    else:
        # Equal weight if no evidence
        bull.probability = 0.33
        bear.probability = 0.33
        base.probability = 0.34
    
    # DDScore #13: No hypothesis can be 0% (intellectually dishonest)
    MIN_PROB = 0.05
    bull.probability = max(bull.probability, MIN_PROB)
    bear.probability = max(bear.probability, MIN_PROB)
    base.probability = max(base.probability, MIN_PROB)
    
    # Re-normalize after floor
    total = bull.probability + bear.probability + base.probability
    bull.probability = round(bull.probability / total, 4)
    bear.probability = round(bear.probability / total, 4)
    base.probability = round(base.probability / total, 4)
    
    return {
        "bull": bull.to_dict(),
        "bear": bear.to_dict(),
        "base": base.to_dict(),
        "entity": entity
    }


def format_hypotheses(hypotheses: dict) -> str:
    """Formats hypotheses for display."""
    lines = [
        f"\n{'='*50}",
        f"INVESTMENT HYPOTHESES: {hypotheses['entity']}",
        f"{'='*50}",
        "",
        f"BULL CASE ({hypotheses['bull']['probability']:.0%}):",
        f"  Thesis: {hypotheses['bull']['thesis']}",
        "  Supporting Evidence:"
    ]
    
    for ev in hypotheses['bull']['supporting_evidence']:
        lines.append(f"    + {ev}")
    
    lines.extend([
        "",
        f"BEAR CASE ({hypotheses['bear']['probability']:.0%}):",
        f"  Thesis: {hypotheses['bear']['thesis']}",
        "  Supporting Evidence:"
    ])
    
    for ev in hypotheses['bear']['supporting_evidence']:
        lines.append(f"    + {ev}")
    
    lines.extend([
        "",
        f"BASE CASE ({hypotheses['base']['probability']:.0%}):",
        f"  Thesis: {hypotheses['base']['thesis']}",
        "  Supporting Evidence:"
    ])
    
    for ev in hypotheses['base']['supporting_evidence']:
        lines.append(f"    + {ev}")
    
    lines.append(f"\n{'='*50}")
    
    return "\n".join(lines)