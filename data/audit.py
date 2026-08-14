"""
data/audit.py
Phase 9 — Audit Trail & Backtesting

Core functions:
- save_session(): Persist a completed research session
- record_outcome(): Compare historical session against actual market prices
- get_accuracy_stats(): Aggregate accuracy for --audit display
"""

import json
import logging
from datetime import datetime, timedelta, timezone

import numpy as np

from data.db import get_connection
from data.fetcher import fetch_stock_data

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# JSON SERIALIZATION (handles numpy types from EvidenceRegister)
# ═══════════════════════════════════════════════════════════════════════════════

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# ═══════════════════════════════════════════════════════════════════════════════
# SCORING FORMULA
# ═══════════════════════════════════════════════════════════════════════════════

def score_outcome(bias, price_change_30d):
    """
    Graded accuracy score from -1.0 (completely wrong) to +1.0 (perfect).
    """
    if bias == "bullish":
        return round(max(-1.0, min(1.0, price_change_30d / 5.0)), 4)
    elif bias == "bearish":
        return round(max(-1.0, min(1.0, -price_change_30d / 5.0)), 4)
    else:  # neutral
        if abs(price_change_30d) <= 2.0:
            return 1.0
        else:
            return round(max(-1.0, 1.0 - (abs(price_change_30d) - 2.0) / 5.0), 4)


def compute_evidence_strength(bull_strength, bear_strength):
    """Bucket evidence strength for grouping."""
    total = bull_strength + bear_strength
    if total < 0.5:
        return "Speculative"
    elif total < 1.5:
        return "Tentative"
    else:
        return "Convicted"


# ═══════════════════════════════════════════════════════════════════════════════
# SAVE SESSION
# ═══════════════════════════════════════════════════════════════════════════════

def save_session(results, report_path, sector=None):
    """
    Persist a completed research session to the database.
    
    Args:
        results: Dict from EvidenceDrivenLoop._final_output()
        report_path: Path to generated report (str or None)
        sector: Optional sector tag (canonical string or None)
    
    Returns:
        int: session_id
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Extract hypothesis data
    hyp = results.get("hypotheses", {})
    bias = hyp.get("directional_bias", {})
    unc = hyp.get("uncertainty", {})
    
    # Serialize evidence snapshot (handle numpy types)
    snapshot = results.get("evidence_snapshot", {})
    snapshot_json = json.dumps(snapshot, cls=NumpyEncoder, default=str)
    
    now = datetime.now(timezone.utc)
    
    cursor.execute("""
        INSERT INTO research_sessions 
        (entity, ticker, asset_type, sector, session_date, directional_bias,
         uncertainty_score, uncertainty_level, bull_strength, bear_strength,
         evidence_count, halt_reason, iterations, report_path, evidence_snapshot)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        results.get("entity", "unknown"),
        results.get("ticker"),
        results.get("asset_type", "unknown"),
        sector,
        now.strftime("%Y-%m-%d"),
        bias.get("net", "unknown"),
        unc.get("score", 0.0),
        unc.get("level", "Unknown"),
        bias.get("bull_strength", 0.0),
        bias.get("bear_strength", 0.0),
        results.get("evidence_count", 0),
        results.get("halt_reason"),
        results.get("iterations", 0),
        str(report_path) if report_path else None,
        snapshot_json,
    ))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"Saved research session {session_id} for {results.get('entity')}")
    return session_id


# ═══════════════════════════════════════════════════════════════════════════════
# RECORD OUTCOME
# ═══════════════════════════════════════════════════════════════════════════════

def record_outcome(session_id, ticker):
    """
    Compare a historical session against actual 30-day market outcomes.
    
    Args:
        session_id: FK to research_sessions.id
        ticker: Stock/crypto ticker for price lookup
    
    Returns:
        dict: Outcome data, or {"status": "pending"} if < 30 days old
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Fetch session details
    cursor.execute(
        "SELECT * FROM research_sessions WHERE id = ?", (session_id,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"status": "failed", "reason": f"Session {session_id} not found"}
    
    session = dict(row)
    session_date = datetime.strptime(session["session_date"], "%Y-%m-%d").date()
    bias = session["directional_bias"]
    
    # Check if 30 days have passed
    today = datetime.now(timezone.utc).date()
    check_date = session_date + timedelta(days=30)
    if today < check_date:
        conn.close()
        return {"status": "pending", "reason": f"Check date {check_date} not reached yet"}
    
    # Check if outcome already exists
    cursor.execute(
        "SELECT id FROM research_outcomes WHERE session_id = ?", (session_id,)
    )
    if cursor.fetchone():
        conn.close()
        return {"status": "already_recorded", "reason": "Outcome already exists"}
    
    # Fetch prices
    try:
        # Baseline price (session date, 5-day window for weekends/holidays)
        baseline_end = session_date + timedelta(days=5)
        baseline_df = fetch_stock_data(
            ticker, start=str(session_date), end=str(baseline_end)
        )
        if baseline_df.empty:
            raise ValueError("No baseline price data")
        baseline_price = float(baseline_df["Close"].iloc[0])
        
        # 30-day price
        end_start = session_date + timedelta(days=30)
        end_end = session_date + timedelta(days=35)
        end_df = fetch_stock_data(
            ticker, start=str(end_start), end=str(end_end)
        )
        if end_df.empty:
            raise ValueError("No 30-day price data")
        end_price = float(end_df["Close"].iloc[0])
        
        price_change_30d = ((end_price - baseline_price) / baseline_price) * 100
        
        # Determine direction
        if price_change_30d > 1.0:
            actual_direction = "up"
        elif price_change_30d < -1.0:
            actual_direction = "down"
        else:
            actual_direction = "flat"
        
        # Score
        accuracy = score_outcome(bias, price_change_30d)
        bias_correct = (
            (bias == "bullish" and price_change_30d > 0) or
            (bias == "bearish" and price_change_30d < 0) or
            (bias == "neutral" and abs(price_change_30d) <= 2.0)
        )
        
        now = datetime.now(timezone.utc).isoformat()
        
        cursor.execute("""
            INSERT INTO research_outcomes
            (session_id, check_date, actual_direction, price_change_30d,
             bias_was_correct, accuracy_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            now,
            actual_direction,
            round(price_change_30d, 4),
            bias_correct,
            round(accuracy, 4),
            f"Baseline: {baseline_price:.2f}, End: {end_price:.2f}",
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "recorded",
            "session_id": session_id,
            "price_change_30d": round(price_change_30d, 2),
            "accuracy_score": round(accuracy, 4),
            "actual_direction": actual_direction,
        }
        
    except Exception as e:
        conn.close()
        logger.error(f"Failed to record outcome for session {session_id}: {e}")
        return {"status": "failed", "reason": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# GET ACCURACY STATS
# ═══════════════════════════════════════════════════════════════════════════════

def get_accuracy_stats():
    """
    Aggregate historical accuracy for audit display.
    
    Returns:
        dict with grouped statistics
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total sessions
    cursor.execute("SELECT COUNT(*) FROM research_sessions")
    total_sessions = cursor.fetchone()[0]
    
    # Scored sessions
    cursor.execute("""
        SELECT COUNT(*) FROM research_outcomes 
        WHERE accuracy_score IS NOT NULL
    """)
    scored_sessions = cursor.fetchone()[0]
    
    # Pending sessions (older than 30 days but no outcome)
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*) FROM research_sessions 
        WHERE session_date <= ? 
        AND id NOT IN (SELECT session_id FROM research_outcomes)
    """, (thirty_days_ago,))
    pending_sessions = cursor.fetchone()[0]
    
    # Overall average score
    cursor.execute("""
        SELECT AVG(accuracy_score) FROM research_outcomes 
        WHERE accuracy_score IS NOT NULL
    """)
    overall_avg = cursor.fetchone()[0] or 0.0
    
    # By asset type
    cursor.execute("""
        SELECT rs.asset_type, COUNT(*), AVG(ro.accuracy_score)
        FROM research_sessions rs
        JOIN research_outcomes ro ON rs.id = ro.session_id
        WHERE ro.accuracy_score IS NOT NULL
        GROUP BY rs.asset_type
    """)
    by_asset_type = {
        row["asset_type"]: {"count": row[1], "avg_score": round(row[2], 4) if row[2] else 0.0}
        for row in cursor.fetchall()
    }
    
    # By uncertainty level
    cursor.execute("""
        SELECT rs.uncertainty_level, COUNT(*), AVG(ro.accuracy_score)
        FROM research_sessions rs
        JOIN research_outcomes ro ON rs.id = ro.session_id
        WHERE ro.accuracy_score IS NOT NULL
        GROUP BY rs.uncertainty_level
    """)
    by_uncertainty = {
        row["uncertainty_level"]: {"count": row[1], "avg_score": round(row[2], 4) if row[2] else 0.0}
        for row in cursor.fetchall()
    }
    
    # By evidence strength (computed from bull+bear)
    cursor.execute("""
        SELECT rs.bull_strength, rs.bear_strength, ro.accuracy_score
        FROM research_sessions rs
        JOIN research_outcomes ro ON rs.id = ro.session_id
        WHERE ro.accuracy_score IS NOT NULL
    """)
    strength_buckets = {"Speculative": [], "Tentative": [], "Convicted": []}
    for row in cursor.fetchall():
        bucket = compute_evidence_strength(row["bull_strength"], row["bear_strength"])
        strength_buckets[bucket].append(row["accuracy_score"])
    
    by_evidence_strength = {
        bucket: {
            "count": len(scores),
            "avg_score": round(sum(scores) / len(scores), 4) if scores else 0.0
        }
        for bucket, scores in strength_buckets.items()
    }
    
    # By sector (only where sector is not NULL)
    cursor.execute("""
        SELECT rs.sector, COUNT(*), AVG(ro.accuracy_score)
        FROM research_sessions rs
        JOIN research_outcomes ro ON rs.id = ro.session_id
        WHERE ro.accuracy_score IS NOT NULL AND rs.sector IS NOT NULL
        GROUP BY rs.sector
    """)
    by_sector = {
        row["sector"]: {"count": row[1], "avg_score": round(row[2], 4) if row[2] else 0.0}
        for row in cursor.fetchall()
    }
    
    conn.close()
    
    return {
        "total_sessions": total_sessions,
        "scored_sessions": scored_sessions,
        "pending_sessions": pending_sessions,
        "overall_avg_score": round(overall_avg, 4),
        "by_asset_type": by_asset_type,
        "by_uncertainty": by_uncertainty,
        "by_evidence_strength": by_evidence_strength,
        "by_sector": by_sector,
    }