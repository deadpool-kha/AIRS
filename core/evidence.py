"""
core/evidence.py
Issue #9b: Evidence-Driven Loop Evolution

Simple in-memory evidence accumulator with provenance tracking.
No database, no microservices.

Tracks:
- value: the actual evidence data
- source: which agent produced it
- tier: quant computation tier (1, 2, or 3)
- data_points: how many data points the feature was computed from
- data_period: the data depth period (e.g., "3mo", "6mo", "1y")
- timestamp: when it was added
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class EvidenceItem:
    """A single piece of evidence with full provenance metadata."""
    value: Any
    source: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tier: Optional[int] = None
    data_points: Optional[int] = None
    data_period: Optional[str] = None


class EvidenceRegister:
    """
    Central evidence accumulator for AIRS.

    MVP: plain Python dict with typed helpers.
    No persistence, no database tables, no external services.
    """

    def __init__(self):
        self._store: Dict[str, EvidenceItem] = {}

    def add(self, key: str, value: Any, source: str = "unknown",
            tier: Optional[int] = None, data_points: Optional[int] = None,
            data_period: Optional[str] = None) -> None:
        """Add evidence to the register. Overwrites existing entry."""
        self._store[key] = EvidenceItem(
            value=value,
            source=source,
            tier=tier,
            data_points=data_points,
            data_period=data_period
        )

    def get(self, key: str) -> Any:
        """Get evidence value by key. Raises KeyError if missing."""
        if key not in self._store:
            raise KeyError(
                f"Evidence '{key}' not found. Available: {list(self._store.keys())}"
            )
        return self._store[key].value

    def get_meta(self, key: str) -> EvidenceItem:
        """Get full evidence metadata."""
        if key not in self._store:
            raise KeyError(f"Evidence '{key}' not found")
        return self._store[key]

    def has(self, key: str) -> bool:
        return key in self._store

    def get_missing(self, required_keys: List[str]) -> List[str]:
        """Return required keys NOT present in the register."""
        return [k for k in required_keys if k not in self._store]

    def is_trustworthy(self, key: str, min_data_points: int) -> bool:
        """
        Check if evidence is present AND computed from sufficient data.

        Args:
            key: Evidence key
            min_data_points: Minimum data points required for trustworthiness

        Returns:
            True if present and data_points >= min_data_points
            False if missing OR insufficient data depth
        """
        if key not in self._store:
            return False
        item = self._store[key]
        if item.data_points is None:
            return True  # Non-quant evidence (business, technical) is always trustworthy if present
        return item.data_points >= min_data_points

    def get_untrustworthy(self, required_keys: List[str], min_data_points: int) -> List[str]:
        """Return keys that are present but NOT trustworthy (insufficient data depth)."""
        untrustworthy = []
        for k in required_keys:
            if k in self._store:
                item = self._store[k]
                if item.data_points is not None and item.data_points < min_data_points:
                    untrustworthy.append(k)
        return untrustworthy

    def snapshot(self, exclude_types: tuple = ()) -> Dict[str, Any]:
        """Return flat dict of all evidence values (no metadata)."""
        result = {}
        for k, v in self._store.items():
            if exclude_types and type(v.value).__name__ in exclude_types:
                continue
            result[k] = v.value
        return result

    def list_by_source(self, source: str) -> Dict[str, Any]:
        return {k: v.value for k, v in self._store.items() if v.source == source}

    def list_by_tier(self, tier: int) -> Dict[str, Any]:
        return {k: v.value for k, v in self._store.items() if v.tier == tier}

    def keys(self) -> List[str]:
        return list(self._store.keys())

    def __len__(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return f"EvidenceRegister({len(self._store)} items: {list(self._store.keys())})"

    def __contains__(self, key: str) -> bool:
        return key in self._store