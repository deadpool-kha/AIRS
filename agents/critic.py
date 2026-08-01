"""
agents/critic.py
Issue #9b+: Evidence-Driven Loop Evolution — Critic Redesign

The Critic is now a phased research director, not a checklist auditor.

Phases:
  1. INVENTORY:    What evidence do we actually have?
  2. SIGNALS:       What story is each dimension telling? (bullish/bearish/neutral)
  3. DASHBOARD:     Auditable multi-dimensional confidence (Data Quality, Coverage, Agreement, Stability)
  4. CONTRADICTIONS: Where do dimensions disagree?
  5. ACTIVE QUESTIONS: What specific questions need answers?
  6. HALT DECISION: Should we stop? (iteration-aware)

Backward compatibility:
  All legacy keys (missing_evidence, confidence, should_iterate, etc.)
  are still returned so loop.py doesn't break. They are now DERIVED from
  the new phased logic, not computed independently.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple

from utils.ollama_client import OllamaClient
from core.evidence import EvidenceRegister

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# ASSET PROFILES (unchanged — asset-type-aware sufficiency)
# ═══════════════════════════════════════════════════════════════════════════════

ASSET_PROFILES = {
    "public_stock": {
        "required_dimensions": ["quant", "business"],
        "optional_dimensions": ["technical"],
        "impossible_dimensions": [],
        "quant_min_days": 90,
        "business_min_articles": 8,
        "description": "Publicly traded company with stock ticker",
    },
    "crypto_with_repo": {
        "required_dimensions": ["quant", "technical", "business"],
        "optional_dimensions": [],
        "impossible_dimensions": [],
        "quant_min_days": 180,
        "technical_min_commits": 50,
        "business_min_articles": 8,
        "description": "Crypto project with traded token and public repository",
    },
    "open_source_or_pre_launch": {
        "required_dimensions": ["technical", "business"],
        "optional_dimensions": ["quant"],
        "impossible_dimensions": ["quant"],
        "technical_min_commits": 30,
        "business_min_articles": 5,
        "description": "Open-source project or pre-launch startup (no token/stock)",
    },
    "private_company": {
        "required_dimensions": ["business"],
        "optional_dimensions": ["technical", "quant"],
        "impossible_dimensions": ["quant", "technical"],
        "business_min_articles": 10,
        "description": "Private company with no public financials or code",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE TRUSTWORTHINESS (minimum data points for statistical validity)
# ═══════════════════════════════════════════════════════════════════════════════

FEATURE_TRUSTWORTHINESS = {
    "returns": {"min_data_points": 5},
    "volatility": {"min_data_points": 20},
    "momentum": {"min_data_points": 30},
    "moving_averages": {"min_data_points": 50},
    "drawdown": {"min_data_points": 30},
    "risk_score": {"min_data_points": 20},
    "trend": {"min_data_points": 50},
    "current_price": {"min_data_points": 1},
    "data_points": {"min_data_points": 1},
    "rsi": {"min_data_points": 20},
    "macd": {"min_data_points": 40},
    "volume_profile": {"min_data_points": 20},
    "atr": {"min_data_points": 20},
    "volatility_regime": {"min_data_points": 90},
    "beta": {"min_data_points": 90},
    "correlation_matrix": {"min_data_points": 180},
}

DIMENSION_FEATURES = {
    "quant": ["returns", "volatility", "momentum", "moving_averages", "drawdown",
              "risk_score", "trend", "current_price", "data_points", "rsi", "macd",
              "volume_profile", "atr", "volatility_regime", "beta", "correlation_matrix"],
    "technical": ["technical_context"],
    "business": ["business_context"],
}

# ═══════════════════════════════════════════════════════════════════════════════
# CONTRADICTION RULES (hardcoded — now with active question mapping)
# ═══════════════════════════════════════════════════════════════════════════════

CONTRADICTION_RULES = [
    {
        "name": "price_up_fundamentals_down",
        "description": "Price trending up but business signals are negative",
        "severity": "high",
        "check": lambda r: (
            r.has("trend") and r.get("trend") in ["uptrend", "strong_uptrend"] and
            r.has("business_context") and _count_negative_signals(r.get("business_context")) > 3
        ),
        "active_question": "Is price momentum sustainable against weak fundamentals?",
        "why_it_matters": "A rally without fundamental support often collapses. Need to know if this is a dead-cat bounce.",
        "evidence_needed": ["drawdown", "momentum", "volume_profile"],
        "can_deeper_data_resolve": True,
        "rationale": "Need longer history to see if trend holds against fundamentals",
    },
    {
        "name": "price_up_repo_dead",
        "description": "Price trending up but development has stalled",
        "severity": "high",
        "check": lambda r: (
            r.has("trend") and r.get("trend") in ["uptrend", "strong_uptrend"] and
            r.has("technical_context") and _get_technical_metric(r.get("technical_context"), "days_since_commit", 0) > 30
        ),
        "active_question": "Is price action disconnected from engineering reality?",
        "why_it_matters": "Speculative pumps often occur when development stops but marketing continues.",
        "evidence_needed": ["technical_context"],  # Already have it, but flag for human review
        "can_deeper_data_resolve": False,
        "rationale": "Price pump without engineering activity — need more business context",
    },
    {
        "name": "high_risk_positive_news",
        "description": "High quantitative risk but positive business coverage",
        "severity": "medium",
        "check": lambda r: (
            r.has("risk_score") and r.get("risk_score") > 0.7 and
            r.has("business_context") and _count_positive_signals(r.get("business_context")) > 5
        ),
        "active_question": "Is the market pricing in risks that the news cycle is ignoring?",
        "why_it_matters": "Quantitative stress (volatility, drawdown) may precede business headlines by weeks.",
        "evidence_needed": ["volatility_regime", "drawdown"],
        "can_deeper_data_resolve": True,
        "rationale": "Are developers actually delivering despite the risk?",
    },
    {
        "name": "oversold_but_downtrend",
        "description": "RSI shows oversold but trend is still down",
        "severity": "medium",
        "check": lambda r: (
            r.has("rsi") and r.get("rsi") < 30 and
            r.has("trend") and r.get("trend") in ["downtrend", "strong_downtrend"]
        ),
        "active_question": "Falling knife or genuine bottom?",
        "why_it_matters": "Oversold bounces can trap buyers if the structural trend hasn't changed.",
        "evidence_needed": ["drawdown", "momentum", "volatility_regime"],
        "can_deeper_data_resolve": True,
        "rationale": "Falling knife or bottom? Need more history to tell.",
    },
    {
        "name": "high_volume_flat_price",
        "description": "Volume spiking but price not moving",
        "severity": "medium",
        "check": lambda r: (
            r.has("volume_profile") and _get_nested(r.get("volume_profile"), "relative_volume", 0) > 2.0 and
            r.has("momentum") and abs(_get_nested(r.get("momentum"), "5d", 0)) < 0.02
        ),
        "active_question": "Is this accumulation or distribution?",
        "why_it_matters": "High volume without price movement often signals smart money exiting quietly.",
        "evidence_needed": ["volume_profile", "drawdown"],
        "can_deeper_data_resolve": True,
        "rationale": "Distribution phase? Need longer history to confirm.",
    },
    {
        "name": "hype_vs_delivery",
        "description": "Positive news but no recent development activity",
        "severity": "high",
        "check": lambda r: (
            r.has("business_context") and _count_positive_signals(r.get("business_context")) > 5 and
            r.has("technical_context") and _get_technical_metric(r.get("technical_context"), "days_since_commit", 0) > 30
        ),
        "active_question": "Is marketing running ahead of engineering?",
        "why_it_matters": "A widening gap between hype and delivery is a classic pre-collapse pattern.",
        "evidence_needed": ["technical_context"],
        "can_deeper_data_resolve": False,
        "rationale": "Marketing running but engineering stopped — pivot or abandonment?",
    },
    {
        "name": "great_product_no_market",
        "description": "Healthy codebase but no business traction",
        "severity": "medium",
        "check": lambda r: (
            r.has("technical_context") and _get_technical_metric(r.get("technical_context"), "health_score", 0) > 0.8 and
            r.has("business_context") and _count_catalysts(r.get("business_context")) == 0 and
            _count_signals(r.get("business_context")) < 3
        ),
        "active_question": "Is this a solution in search of a problem?",
        "why_it_matters": "Beautiful code with no users is a hobby, not an investment.",
        "evidence_needed": ["business_context"],
        "can_deeper_data_resolve": False,
        "rationale": "Code is beautiful but nobody cares — search broader for adoption signals",
    },
    {
        "name": "value_trap",
        "description": "Positive fundamentals but price keeps falling",
        "severity": "high",
        "check": lambda r: (
            r.has("trend") and r.get("trend") in ["downtrend", "strong_downtrend"] and
            r.has("business_context") and _count_positive_signals(r.get("business_context")) > 3
        ),
        "active_question": "Does the market know something the fundamentals don't show?",
        "why_it_matters": "When price and fundamentals diverge, price is usually the leading indicator.",
        "evidence_needed": ["drawdown", "volatility_regime", "beta"],
        "can_deeper_data_resolve": True,
        "rationale": "Market knows something you don't. Need 1y history to see damage.",
    },
    {
        "name": "sell_the_news",
        "description": "Major catalyst announced but price dropped on volume",
        "severity": "medium",
        "check": lambda r: (
            r.has("business_context") and _has_catalyst_keyword(r.get("business_context")) and
            r.has("trend") and r.get("trend") == "downtrend" and
            r.has("volume_profile") and _get_nested(r.get("volume_profile"), "volume_trend", "") == "increasing"
        ),
        "active_question": "Was the catalyst already priced in?",
        "why_it_matters": "Buy-the-rumor-sell-the-news is one of the most reliable patterns in markets.",
        "evidence_needed": ["volume_profile", "momentum"],
        "can_deeper_data_resolve": True,
        "rationale": "Classic buy-the-rumor-sell-the-news. Check pre vs post event.",
    },
    {
        "name": "zombie_project",
        "description": "No development but news remains neutral/positive",
        "severity": "high",
        "check": lambda r: (
            r.has("technical_context") and _get_technical_metric(r.get("technical_context"), "days_since_commit", 0) > 60 and
            r.has("business_context") and _count_negative_signals(r.get("business_context")) == 0
        ),
        "active_question": "Is this project coasting on past reputation?",
        "why_it_matters": "Ghost projects can maintain positive news cycles for months while silently dying.",
        "evidence_needed": ["technical_context"],
        "can_deeper_data_resolve": False,
        "rationale": "Ghost project riding old hype? Verify news is actually about this project.",
    },
    {
        "name": "low_vol_high_risk",
        "description": "Low volatility but high risk score suggests hidden drawdown",
        "severity": "medium",
        "check": lambda r: (
            r.has("volatility") and r.get("volatility") < 0.2 and
            r.has("risk_score") and r.get("risk_score") > 0.6
        ),
        "active_question": "Is the price stable because it already crashed?",
        "why_it_matters": "Low volatility after a drawdown is not safety — it's exhaustion.",
        "evidence_needed": ["drawdown", "atr"],
        "can_deeper_data_resolve": True,
        "rationale": "Price looks stable because it already crashed. See full 1y damage.",
    },
    {
        "name": "overbought_stale_dev",
        "description": "Price overbought but developers inactive",
        "severity": "high",
        "check": lambda r: (
            r.has("rsi") and r.get("rsi") > 75 and
            r.has("technical_context") and _get_technical_metric(r.get("technical_context"), "days_since_commit", 0) > 21
        ),
        "active_question": "Is this a speculative pump with no engineering foundation?",
        "why_it_matters": "Overbought + stale repos are a hallmark of exit scams or abandoned pumps.",
        "evidence_needed": ["technical_context", "volume_profile"],
        "can_deeper_data_resolve": False,
        "rationale": "Speculative pump with no fundamentals. Who is driving price?",
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_nested(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _count_signals(business_data: dict) -> int:
    return _get_nested(_get_nested(business_data, "metrics", {}), "signal_count", 0)


def _count_positive_signals(business_data: dict) -> int:
    return _get_nested(_get_nested(business_data, "metrics", {}), "positive_signals", 0)


def _count_negative_signals(business_data: dict) -> int:
    return _get_nested(_get_nested(business_data, "metrics", {}), "negative_signals", 0)


def _count_catalysts(business_data: dict) -> int:
    return _get_nested(_get_nested(business_data, "metrics", {}), "catalyst_count", 0)


def _get_technical_metric(technical_data: dict, metric: str, default: Any = None) -> Any:
    return _get_nested(_get_nested(technical_data, "metrics", {}), metric, default)


def _has_catalyst_keyword(business_data: dict) -> bool:
    catalysts = business_data.get("catalysts", []) if isinstance(business_data, dict) else []
    keywords = ["launch", "partnership", "release", "announcement", "listing"]
    return any(kw in str(c).lower() for c in catalysts for kw in keywords)


# ═══════════════════════════════════════════════════════════════════════════════
# CRITIC AGENT CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class CriticAgent:
    """
    Context-aware evidence auditor and research director.

    100% rule-based. No LLM decides what features to compute or when to halt.
    LLM is ONLY used for optional qualitative suggestions (evaluate_evidence_with_llm).
    """

    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.ollama = ollama_client or OllamaClient()

    # ═══════════════════════════════════════════════════════════════════════
    # PRIMARY METHOD: evaluate_evidence (NEW ARCHITECTURE)
    # ═══════════════════════════════════════════════════════════════════════

    def evaluate_evidence(
        self,
        entity: str,
        evidence_register: EvidenceRegister,
        asset_profile: dict,
        iteration: int = 1,
        previous_critic_output: Optional[dict] = None,
    ) -> dict:
        """
        Audit the Evidence Register using the phased analyst model.

        Args:
            entity: Company or asset name
            evidence_register: The shared evidence register
            asset_profile: Dict from capability probe with asset_type, available dims, etc.
            iteration: Current loop iteration (1-3)
            previous_critic_output: Output from iteration-1 (for stability tracking)

        Returns:
            Dict with dashboard, active_questions, halt_decision, and backward-compatible keys.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info(
            f"Critic auditing {entity} (iteration {iteration}, profile={asset_profile.get('asset_type')})"
        )

        # ── Phase 1: Inventory ─────────────────────────────────────────────
        inventory = self._inventory(evidence_register, asset_profile)

        # ── Phase 2: Directional Signals ───────────────────────────────────
        signals = self._extract_directional_signals(evidence_register, inventory)

        # ── Phase 3: Dashboard ─────────────────────────────────────────────
        dashboard = self._compute_dashboard(
            evidence_register, inventory, signals, iteration, previous_critic_output
        )

        # ── Phase 4: Contradictions ────────────────────────────────────────
        contradictions = self._detect_contradictions(evidence_register)
        resolvable, unresolved = self._classify_contradictions(contradictions, iteration)

        # ── Phase 5: Active Questions ────────────────────────────────────
        active_questions = self._formulate_active_questions(
            inventory, signals, contradictions, iteration
        )

        # ── Phase 6: Halt Decision ─────────────────────────────────────────
        halt = self._decide_halt(
            inventory, dashboard, contradictions, active_questions, iteration
        )

        # ── Backward-compatible derivations ────────────────────────────────
        missing_evidence = self._derive_missing_evidence(active_questions, inventory)
        confidence = self._derive_confidence(dashboard)

        logger.info(
            f"Critic audit: halt={not halt['should_iterate']}, reason={halt['reason']}, "
            f"dashboard={dashboard['agreement']['level']}/{dashboard['stability']['level']}"
        )

        return {
            # ── NEW ARCHITECTURE (primary) ──
            "dashboard": dashboard,
            "active_questions": active_questions,
            "signals": signals,
            "inventory": inventory,
            "halt_decision": halt,

            # ── BACKWARD COMPATIBILITY (for loop.py) ──
            "agent": "critic",
            "entity": entity,
            "timestamp": timestamp,
            "iteration": iteration,
            "asset_type": asset_profile.get("asset_type", "unknown"),
            "missing_evidence": missing_evidence,
            "confidence": round(confidence, 4),
            "recommendation": halt["recommendation"],
            "should_iterate": halt["should_iterate"],
            "resolvable_contradictions": resolvable,
            "unresolved_contradictions": unresolved,
            "contradictions": contradictions,
            "present_features": inventory["present_features"],
            "dimension_gaps": inventory["dimension_gaps"],
            "available_dimensions": inventory["available_dims"],
            "impossible_dimensions": inventory["impossible_dims"],
            "unavailable_dimensions": inventory["unavailable_dims"],
            "required_features": inventory["required_features"],
            "evidence_count": len(evidence_register),
            "status": "complete",
            "sources": ["rule_based", "evidence_register_audit", "contradiction_detection", "directional_analysis"],
        }

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 1: INVENTORY
    # ═══════════════════════════════════════════════════════════════════════

    def _inventory(self, register: EvidenceRegister, asset_profile: dict) -> dict:
        """Catalog what evidence exists, what's missing, and what's impossible."""
        asset_type = asset_profile.get("asset_type", "unknown")
        profile_rules = ASSET_PROFILES.get(asset_type, ASSET_PROFILES["private_company"])

        # Available vs impossible dimensions
        available_dims = []
        impossible_dims = []
        unavailable_dims = []

        for dim in ["quant", "technical", "business"]:
            key = f"{dim}_available"
            if asset_profile.get(key):
                available_dims.append(dim)
            elif dim in profile_rules.get("impossible_dimensions", []):
                impossible_dims.append(dim)
            else:
                unavailable_dims.append(dim)

        # Build required feature list from available dimensions only
        required_features = []
        for dim in available_dims:
            required_features.extend(DIMENSION_FEATURES.get(dim, []))
        required_features = list(dict.fromkeys(required_features))

        # Check presence and trustworthiness
        present_features = []
        missing_features = []
        untrustworthy_features = []

        for feature in required_features:
            if not register.has(feature):
                missing_features.append(feature)
                continue
            present_features.append(feature)
            trust_rule = FEATURE_TRUSTWORTHINESS.get(feature, {})
            min_points = trust_rule.get("min_data_points", 1)
            if not register.is_trustworthy(feature, min_points):
                meta = register.get_meta(feature)
                untrustworthy_features.append({
                    "feature": feature,
                    "has_data_points": meta.data_points,
                    "needs_data_points": min_points,
                })
                missing_features.append(feature)

        # Dimension-level gaps
        dimension_gaps = []
        if "quant" in available_dims:
            quant_data = register.list_by_source("quant")
            if not quant_data:
                dimension_gaps.append("quant_no_evidence")
            elif "price_data" not in quant_data:
                dimension_gaps.append("quant_no_price_data")

        if "technical" in available_dims and not register.has("technical_context"):
            dimension_gaps.append("technical_missing")

        if "business" in available_dims:
            if not register.has("business_context"):
                dimension_gaps.append("business_missing")
            else:
                biz = register.get("business_context")
                article_count = len(biz.get("raw_articles", [])) if isinstance(biz, dict) else 0
                min_articles = profile_rules.get("business_min_articles", 8)
                if article_count < min_articles:
                    dimension_gaps.append(f"business_insufficient_articles ({article_count}/{min_articles})")

        return {
            "available_dims": available_dims,
            "impossible_dims": impossible_dims,
            "unavailable_dims": unavailable_dims,
            "required_features": required_features,
            "present_features": present_features,
            "missing_features": missing_features,
            "untrustworthy_features": untrustworthy_features,
            "dimension_gaps": dimension_gaps,
            "profile_rules": profile_rules,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 2: DIRECTIONAL SIGNALS
    # ═══════════════════════════════════════════════════════════════════════

    def _extract_directional_signals(
        self, register: EvidenceRegister, inventory: dict
    ) -> dict:
        """
        Extract a directional 'vote' from each available dimension.
        Maps everything to a unified space: positive / negative / neutral / unknown.
        """
        signals = {}

        # ── Quant ──
        if "quant" in inventory["available_dims"] and register.has("trend"):
            trend = register.get("trend")
            if trend in ["strong_uptrend", "uptrend"]:
                signals["quant"] = {"raw": trend, "unified": "positive", "strength": "moderate"}
            elif trend in ["strong_downtrend", "downtrend"]:
                signals["quant"] = {"raw": trend, "unified": "negative", "strength": "moderate"}
            else:
                signals["quant"] = {"raw": trend, "unified": "neutral", "strength": "weak"}
        else:
            signals["quant"] = {"raw": "missing", "unified": "unknown", "strength": "none"}

        # ── Business ──
        if "business" in inventory["available_dims"] and register.has("business_context"):
            biz = register.get("business_context")
            pos = _count_positive_signals(biz)
            neg = _count_negative_signals(biz)
            net = pos - neg
            if net > 1:
                signals["business"] = {"raw": f"+{pos}/-{neg}", "unified": "positive", "strength": "moderate" if pos > 3 else "weak"}
            elif net < -1:
                signals["business"] = {"raw": f"+{pos}/-{neg}", "unified": "negative", "strength": "moderate" if neg > 3 else "weak"}
            else:
                signals["business"] = {"raw": f"+{pos}/-{neg}", "unified": "neutral", "strength": "weak"}
        else:
            signals["business"] = {"raw": "missing", "unified": "unknown", "strength": "none"}

        # ── Technical ──
        if "technical" in inventory["available_dims"] and register.has("technical_context"):
            health = _get_technical_metric(register.get("technical_context"), "health_score", 0)
            days = _get_technical_metric(register.get("technical_context"), "days_since_commit", 999)
            if health > 0.6 and days <= 14:
                signals["technical"] = {"raw": f"health={health:.2f}", "unified": "positive", "strength": "moderate"}
            elif health < 0.4 or days > 30:
                signals["technical"] = {"raw": f"health={health:.2f}", "unified": "negative", "strength": "moderate"}
            else:
                signals["technical"] = {"raw": f"health={health:.2f}", "unified": "neutral", "strength": "weak"}
        else:
            signals["technical"] = {"raw": "missing", "unified": "unknown", "strength": "none"}

        # ── Risk (derived from quant, but treated as its own signal) ──
        if register.has("risk_score"):
            rs = register.get("risk_score")
            if isinstance(rs, (int, float)) and rs > 0.5:
                signals["risk"] = {"raw": f"risk_score={rs:.2f}", "unified": "negative", "strength": "moderate"}
            elif isinstance(rs, (int, float)) and rs > 0.3:
                signals["risk"] = {"raw": f"risk_score={rs:.2f}", "unified": "neutral", "strength": "weak"}
            else:
                signals["risk"] = {"raw": f"risk_score={rs:.2f}", "unified": "positive", "strength": "weak"}
        else:
            signals["risk"] = {"raw": "missing", "unified": "unknown", "strength": "none"}

        return signals

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 3: DASHBOARD
    # ═══════════════════════════════════════════════════════════════════════

    def _compute_dashboard(
        self,
        register: EvidenceRegister,
        inventory: dict,
        signals: dict,
        iteration: int,
        previous: Optional[dict],
    ) -> dict:
        """Build the auditable multi-dimensional confidence dashboard."""

        # ── Data Quality ──
        dq_score = 0.0
        dq_details = {}

        if "quant" in inventory["available_dims"]:
            if register.has("data_points"):
                dp = register.get("data_points")
                if isinstance(dp, int):
                    target = 250  # 1y ≈ 250 trading days
                    dq_details["quant"] = min(dp / target, 1.0)
            elif register.has("price_data"):
                # price_data is a DataFrame
                pd = register.get("price_data")
                if hasattr(pd, "__len__"):
                    dq_details["quant"] = min(len(pd) / 250, 1.0)

        if "business" in inventory["available_dims"] and register.has("business_context"):
            biz = register.get("business_context")
            articles = len(biz.get("raw_articles", [])) if isinstance(biz, dict) else 0
            target = inventory["profile_rules"].get("business_min_articles", 8)
            dq_details["business"] = min(articles / target, 1.0)

        if "technical" in inventory["available_dims"] and register.has("technical_context"):
            tech = register.get("technical_context")
            days = _get_technical_metric(tech, "days_since_commit", 999)
            recency = 1.0 if days <= 7 else 0.7 if days <= 30 else 0.3 if days <= 60 else 0.0
            health = _get_technical_metric(tech, "health_score", 0)
            dq_details["technical"] = (recency + min(health, 1.0)) / 2

        if dq_details:
            dq_score = sum(dq_details.values()) / len(dq_details)

        # ── Coverage ──
        required = set(inventory["required_features"])
        present = set(inventory["present_features"])
        coverage_score = len(present) / len(required) if required else 1.0

        # ── Agreement ──
        unified = [s["unified"] for s in signals.values() if s["unified"] != "unknown"]
        if not unified:
            agreement = {"level": "Unknown", "score": 0.0, "details": "No signals available"}
        else:
            pos = unified.count("positive")
            neg = unified.count("negative")
            neu = unified.count("neutral")
            total = len(unified)

            if pos > 0 and neg == 0:
                level = "High"
                score = 0.8 + (0.2 * (pos / total))
            elif neg > 0 and pos == 0:
                level = "High"
                score = 0.8 + (0.2 * (neg / total))
            elif pos > 0 and neg > 0:
                level = "Low"
                score = 0.3
            else:
                level = "Medium"
                score = 0.5 + (0.3 * (max(pos, neg, neu) / total))

            agreement = {
                "level": level,
                "score": round(min(score, 1.0), 4),
                "details": f"{pos} positive, {neg} negative, {neu} neutral across {total} dimensions",
            }

        # ── Stability ──
        stability = {"level": "Unknown", "score": 0.0, "details": "First iteration — no baseline"}
        if iteration > 1 and previous is not None:
            prev_signals = previous.get("signals", {})
            if prev_signals:
                changes = 0
                for dim, sig in signals.items():
                    prev = prev_signals.get(dim, {})
                    if prev.get("unified") != sig["unified"]:
                        changes += 1
                if changes == 0:
                    stability = {"level": "Stable", "score": 1.0, "details": "No dimension flipped direction"}
                elif changes == 1:
                    stability = {"level": "Emerging", "score": 0.6, "details": "One dimension changed direction"}
                else:
                    stability = {"level": "Shifting", "score": 0.2, "details": f"{changes} dimensions changed direction"}

        return {
            "data_quality": {"score": round(dq_score, 4), "details": dq_details},
            "coverage": {"score": round(coverage_score, 4), "required": len(required), "present": len(present)},
            "agreement": agreement,
            "stability": stability,
            "iteration": iteration,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 4: CONTRADICTIONS
    # ═══════════════════════════════════════════════════════════════════════

    def _detect_contradictions(self, register: EvidenceRegister) -> List[dict]:
        """Run all hardcoded contradiction rules against the register."""
        found = []
        for rule in CONTRADICTION_RULES:
            try:
                if rule["check"](register):
                    found.append({
                        "name": rule["name"],
                        "description": rule["description"],
                        "severity": rule["severity"],
                        "active_question": rule.get("active_question", ""),
                        "why_it_matters": rule.get("why_it_matters", ""),
                        "evidence_needed": rule.get("evidence_needed", []),
                        "can_deeper_data_resolve": rule.get("can_deeper_data_resolve", False),
                        "rationale": rule["rationale"],
                    })
            except Exception as e:
                logger.warning(f"Contradiction rule {rule['name']} failed: {e}")

        # Catch-all: generic cross-dimension tension
        if not found:
            tension = self._detect_cross_dimension_tension(register)
            if tension:
                found.append(tension)

        return found

    def _classify_contradictions(self, contradictions: List[dict], iteration: int) -> Tuple[List[dict], List[dict]]:
        """At iteration 3, nothing is resolvable (circuit breaker)."""
        if iteration >= 3:
            return [], contradictions

        resolvable = [c for c in contradictions if c.get("can_deeper_data_resolve")]
        unresolved = [c for c in contradictions if not c.get("can_deeper_data_resolve")]
        return resolvable, unresolved

    def _detect_cross_dimension_tension(self, register: EvidenceRegister) -> Optional[dict]:
        """Generic catch-all when no specific rule matched."""
        try:
            if (register.has("trend") and register.get("trend") in ["uptrend", "strong_uptrend"] and
                register.has("business_context") and _count_negative_signals(register.get("business_context")) > 0):
                return {
                    "name": "cross_dimension_tension",
                    "description": "Quant signals bullish but business has negative signals",
                    "severity": "low",
                    "active_question": "Is price optimism justified given business headwinds?",
                    "why_it_matters": "Even mild tension can widen into a full contradiction as data deepens.",
                    "evidence_needed": ["drawdown", "momentum"],
                    "can_deeper_data_resolve": True,
                    "rationale": "Mild tension between price action and fundamentals — more data may clarify",
                }

            if (register.has("trend") and register.get("trend") in ["downtrend", "strong_downtrend"] and
                register.has("business_context") and _count_positive_signals(register.get("business_context")) > 2):
                return {
                    "name": "cross_dimension_tension",
                    "description": "Quant signals bearish but business has positive signals",
                    "severity": "low",
                    "active_question": "Is the market overreacting to short-term price action?",
                    "why_it_matters": "Value opportunities often appear when price and fundamentals diverge.",
                    "evidence_needed": ["drawdown", "volatility_regime"],
                    "can_deeper_data_resolve": True,
                    "rationale": "Mild tension between price action and fundamentals — more data may clarify",
                }
        except Exception:
            pass
        return None

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 5: ACTIVE QUESTIONS
    # ═══════════════════════════════════════════════════════════════════════

    def _formulate_active_questions(
        self, inventory: dict, signals: dict, contradictions: List[dict], iteration: int
    ) -> List[dict]:
        """
        Instead of a flat 'missing features' list, return specific research questions.
        The loop continues only to answer questions that deeper data CAN answer.
        """
        questions = []

        # 1. Contradictions that deeper data might resolve
        for c in contradictions:
            if c.get("can_deeper_data_resolve") and iteration < 3:
                questions.append({
                    "question": c["active_question"],
                    "why_it_matters": c["why_it_matters"],
                    "evidence_needed": c["evidence_needed"],
                    "source_contradiction": c["name"],
                    "can_deeper_data_answer": True,
                })

        # 2. Missing features that are blocking coverage
        # Only add these if they would actually change the story
        for f in inventory["missing_features"]:
            # Don't list every missing feature as a "question" — only high-impact ones
            if f in ["drawdown", "risk_score", "trend"] and iteration == 1:
                questions.append({
                    "question": f"Can we establish a baseline directional view without {f}?",
                    "why_it_matters": f"{f} is required for a coherent investment thesis.",
                    "evidence_needed": [f],
                    "source_contradiction": None,
                    "can_deeper_data_answer": True,
                })

        # 3. Low agreement when we have enough coverage
        pos = sum(1 for s in signals.values() if s.get("unified") == "positive")
        neg = sum(1 for s in signals.values() if s.get("unified") == "negative")
        if pos > 0 and neg > 0 and iteration < 3:
            questions.append({
                "question": "Which dimension is the leading indicator — price or fundamentals?",
                "why_it_matters": "Dimensions disagree. Deeper history may reveal which one typically leads.",
                "evidence_needed": ["drawdown", "momentum", "volatility_regime"],
                "source_contradiction": "cross_dimension_tension",
                "can_deeper_data_answer": True,
            })

        return questions

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 6: HALT DECISION (iteration-aware)
    # ═══════════════════════════════════════════════════════════════════════

    def _decide_halt(
        self,
        inventory: dict,
        dashboard: dict,
        contradictions: List[dict],
        active_questions: List[dict],
        iteration: int,
    ) -> dict:
        """
        The loop asks DIFFERENT questions at each iteration:

        Iteration 1: "Can I form a coherent directional view?"
        Iteration 2: "Did deeper data change the story?"
        Iteration 3: Circuit breaker — always halt.
        """

        # ── Circuit Breaker ──
        if iteration >= 3:
            unresolved = [c for c in contradictions if not c.get("can_deeper_data_resolve")]
            reason = "max_iterations"
            if unresolved:
                reason += f" ({len(unresolved)} unresolved contradictions)"
            return {
                "should_iterate": False,
                "reason": reason,
                "recommendation": "complete",
                "narrative": "Circuit breaker hit. Returning best available analysis.",
            }

        # ── Iteration 1: Can we form a coherent view? ──
        if iteration == 1:
            cov = dashboard["coverage"]["score"]
            agr = dashboard["agreement"]["level"]
            high_sev = any(c["severity"] == "high" for c in contradictions)

            # We can halt early if:
            # - We have at least 2 dimensions with evidence
            # - They agree on direction
            # - No critical contradictions
            if cov >= 0.5 and agr == "High" and not high_sev and not active_questions:
                return {
                    "should_iterate": False,
                    "reason": "coherent_view",
                    "recommendation": "complete",
                    "narrative": "All available dimensions agree. Deeper data unlikely to change the thesis.",
                }

            # If agreement is medium and no critical issues, we COULD halt,
            # but let's fetch one deeper tier to see if clarity improves
            if cov >= 0.5 and agr == "Medium" and not high_sev:
                return {
                    "should_iterate": True,
                    "reason": "seeking_clarity",
                    "recommendation": "need_more_data",
                    "narrative": "View is forming but not yet sharp. One deeper tier requested.",
                }

            # Otherwise, we genuinely need more data
            return {
                "should_iterate": True,
                "reason": "insufficient_clarity",
                "recommendation": "need_more_data",
                "narrative": "Cannot form a coherent view yet. Fetching deeper data.",
            }

        # ── Iteration 2: Did the view change? ──
        if iteration == 2:
            stab = dashboard["stability"]["level"]
            agr = dashboard["agreement"]["level"]

            # If the story stabilized, stop
            if stab == "Stable" and agr in ("High", "Medium"):
                return {
                    "should_iterate": False,
                    "reason": "stable_thesis",
                    "recommendation": "complete",
                    "narrative": "Thesis stabilized between tier 1 and tier 2. Additional data unnecessary.",
                }

            # If agreement improved to High, stop
            if agr == "High" and not any(c["severity"] == "high" for c in contradictions):
                return {
                    "should_iterate": False,
                    "reason": "resolved",
                    "recommendation": "complete",
                    "narrative": "Deeper data resolved ambiguity. Thesis is now clear.",
                }

            # If we still have active questions that deeper data CAN answer, go to tier 3
            answerable = [q for q in active_questions if q.get("can_deeper_data_answer")]
            if answerable:
                return {
                    "should_iterate": True,
                    "reason": "unresolved_questions",
                    "recommendation": "need_more_data",
                    "narrative": f"{len(answerable)} research question(s) remain that 1y data may resolve.",
                }

            # Nothing answerable left — stop and flag contradictions as unresolved
            return {
                "should_iterate": False,
                "reason": "unresolvable_tension",
                "recommendation": "complete",
                "narrative": "Contradictions remain but deeper data cannot resolve them. Halting with flags.",
            }

        # Fallback (should never reach here)
        return {
            "should_iterate": False,
            "reason": "fallback",
            "recommendation": "complete",
            "narrative": "Unexpected state. Halting for safety.",
        }

    # ═══════════════════════════════════════════════════════════════════════
    # BACKWARD-COMPATIBLE DERIVATIONS
    # ═══════════════════════════════════════════════════════════════════════

    def _derive_missing_evidence(self, active_questions: List[dict], inventory: dict) -> List[str]:
        """
        Build a legacy-style missing_evidence list from active questions.
        Only includes features that are actually missing AND computable.
        """
        missing = set(inventory["missing_features"])

        # Also include evidence_needed from active questions that are answerable
        for q in active_questions:
            if q.get("can_deeper_data_answer"):
                for feat in q.get("evidence_needed", []):
                    if feat not in inventory["present_features"]:
                        missing.add(feat)

        return sorted(list(missing))

    def _derive_confidence(self, dashboard: dict) -> float:
        """
        Composite confidence from the dashboard dimensions.
        This replaces the old checklist-coverage confidence.
        """
        dq = dashboard["data_quality"]["score"]
        cov = dashboard["coverage"]["score"]
        agr = dashboard["agreement"]["score"]
        stab = dashboard["stability"]["score"] if dashboard["stability"]["level"] != "Unknown" else 0.5

        # Weighted composite: data quality matters most, then agreement
        score = (dq * 0.25) + (cov * 0.25) + (agr * 0.30) + (stab * 0.20)
        return round(min(score, 1.0), 4)

    # ═══════════════════════════════════════════════════════════════════════
    # DISPLAY HELPERS (used by loop.py _display_critic)
    # ═══════════════════════════════════════════════════════════════════════

    def format_dashboard(self, dashboard: dict) -> str:
        """Human-readable dashboard for console output."""
        lines = [
            f"  Data Quality:  {dashboard['data_quality']['score']:.0%}",
            f"  Coverage:      {dashboard['coverage']['score']:.0%} ({dashboard['coverage']['present']}/{dashboard['coverage']['required']} features)",
            f"  Agreement:     {dashboard['agreement']['level']} ({dashboard['agreement']['details']})",
            f"  Stability:     {dashboard['stability']['level']} — {dashboard['stability']['details']}",
        ]
        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════════════
    # OPTIONAL: LLM-Enhanced Critique (read-only, non-binding)
    # ═══════════════════════════════════════════════════════════════════════

    def evaluate_evidence_with_llm(
        self, entity: str, evidence_register: EvidenceRegister,
        asset_profile: dict, iteration: int = 1
    ) -> dict:
        """
        Optional: LLM-enhanced evidence critique.
        Falls back to rule-based if LLM unavailable.
        The LLM suggestion is display-only; it NEVER influences halt logic.
        """
        base = self.evaluate_evidence(entity, evidence_register, asset_profile, iteration)

        if base["halt_decision"]["should_iterate"] is False:
            return base

        summary = self._build_evidence_summary(evidence_register)
        prompt = f"""You are a senior investment analyst reviewing evidence completeness.

Research on: {entity}
Asset type: {asset_profile.get('asset_type', 'unknown')}
Iteration: {iteration}/3

Evidence collected ({base['evidence_count']} items):
{summary}

Active questions:
{chr(10).join([f"- {q['question']}" for q in base['active_questions']]) if base['active_questions'] else 'None — all required evidence present'}

Dashboard:
{self.format_dashboard(base['dashboard'])}

Task: Suggest 1-2 specific, actionable improvements to address gaps or contradictions.
Be concise (2 sentences max). Focus on what data or analysis would strengthen the research.

Improvements:"""

        try:
            response = self.ollama.generate(prompt, timeout=30)
            base["llm_suggestions"] = response.strip()
            base["sources"].append("ollama_reasoning")
        except Exception as e:
            logger.warning(f"LLM critique failed, using rule-based only: {e}")
            base["llm_suggestions"] = None

        return base

    def _build_evidence_summary(self, register: EvidenceRegister) -> str:
        """Build a text summary of evidence for LLM prompt."""
        lines = []
        for source in ["business", "technical", "quant"]:
            items = register.list_by_source(source)
            if items:
                lines.append(f"- {source}: {len(items)} items ({', '.join(items.keys())})")
            else:
                lines.append(f"- {source}: no evidence")
        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════════════
    # LEGACY: Agent-Output-Based Evaluation (preserved for backward compatibility)
    # ═══════════════════════════════════════════════════════════════════════

    def evaluate(self, entity: str, agent_outputs: dict, iteration: int = 1) -> dict:
        """Legacy agent-output-based critique. Preserved for direct use."""
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info(f"Critic Agent evaluating {entity} (iteration {iteration})")

        gaps = []
        recommendations = []
        warnings = []

        quant = agent_outputs.get("quant", {})
        technical = agent_outputs.get("technical", {})
        business = agent_outputs.get("business", {})
        risk = agent_outputs.get("risk", {})

        if quant.get("status") == "skipped":
            pass
        elif quant.get("status") != "complete":
            gaps.append("quant_incomplete")
            recommendations.append("Re-run Quant Agent with valid ticker")
        elif quant.get("confidence", 0) < 0.7:
            gaps.append("quant_low_confidence")
            recommendations.append("Expand data period or verify data source")

        if technical.get("status") == "failed":
            gaps.append("technical_failed")
            recommendations.append("Check GitHub repo name or API rate limits")
        elif technical.get("status") == "skipped":
            pass
        elif technical.get("metrics", {}).get("health_score", 0) == 0:
            gaps.append("technical_no_data")
            recommendations.append("Verify repository exists and is public")

        if business.get("status") == "partial":
            gaps.append("business_insufficient_news")
            recommendations.append("Try alternative news sources or broader ticker")
        elif business.get("status") == "failed":
            gaps.append("business_failed")
            recommendations.append("Check Ollama is running")

        if risk.get("status") != "complete":
            gaps.append("risk_not_evaluated")
            recommendations.append("Run Risk Agent after other agents")
        elif risk.get("metrics", {}).get("risk_count", 0) == 0:
            risk_warnings = risk.get("metrics", {}).get("warning_count", 0)
            if risk_warnings == 0:
                gaps.append("no_risks_identified")
                recommendations.append("Manual risk review recommended")

        quant_conf = quant.get("confidence", 0)
        risk_level = risk.get("metrics", {}).get("overall_risk", "low")
        if quant_conf > 0.8 and risk_level == "high":
            gaps.append("confidence_risk_mismatch")
            recommendations.append("Reconcile high quant confidence with high risk rating")

        if risk_level == "high" and iteration < 3:
            gaps.append("high_risk_not_mitigated")
            recommendations.append("High risk identified — expand risk analysis")

        biz_signals = business.get("signals", [])
        negative_signals = [s for s in biz_signals if s.get("type") == "negative"]
        if len(biz_signals) > 2 and len(negative_signals) == 0:
            warnings.append("business_no_negative_signals")
            recommendations.append("Verify news sources — no negative coverage may indicate bias")

        available = sum([
            1 for k in ["quant", "technical", "business", "risk"]
            if agent_outputs.get(k, {}).get("status") in ["complete", "partial"]
        ])
        if available < 3:
            gaps.append("insufficient_dimensions")
            recommendations.append(f"Only {available}/4 analysis dimensions available")

        total_checks = 8
        passed = total_checks - len(gaps)
        quality_score = round(passed / total_checks, 4)
        should_iterate = len(gaps) > 0 and iteration < 3

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
        """Legacy LLM-enhanced critique."""
        base = self.evaluate(entity, agent_outputs, iteration)

        if base["overall_quality"] == "complete" or not base["should_iterate"]:
            return base

        summary = self._build_legacy_summary(agent_outputs)
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

    def _build_legacy_summary(self, agent_outputs: dict) -> str:
        """Build text summary of agent outputs for LLM prompt."""
        lines = []
        for agent_name, output in agent_outputs.items():
            status = output.get("status", "unknown")
            conf = output.get("confidence", 0)
            lines.append(f"- {agent_name}: status={status}, confidence={conf}")
        return "\n".join(lines)