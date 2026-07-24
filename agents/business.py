"""
agents/business.py

Business Agent for AIRS.
Fetches news, analyzes business signals using local LLM (Ollama).
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

import feedparser

from utils.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class BusinessAgent:
    """Analyzes business signals and news for an entity."""

    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.ollama = ollama_client or OllamaClient()
        self.news_sources = {
            "general": "https://news.google.com/rss/search?q={query}",
            "crypto": "https://cointelegraph.com/rss",
        }

    def analyze(self, entity: str, ticker: Optional[str] = None) -> dict:
        """
        Run business analysis for an entity.

        Args:
            entity: Company or project name (e.g., "NVIDIA", "Ethereum")
            ticker: Optional stock/crypto ticker for better news matching

        Returns:
            Structured business analysis dict
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info(f"Business Agent starting analysis for: {entity}")

        # --- Step 1: Fetch news ---
        raw_articles = self._fetch_news(entity, ticker)
        if not raw_articles:
            logger.warning(f"No news found for {entity}, returning partial analysis")
            return self._build_output(
                entity=entity,
                timestamp=timestamp,
                signals=[],
                summary="No recent news found for this entity.",
                catalysts=[],
                risks=[],
                confidence=0.3,
                status="partial",
                sources=[],
                articles=[],
            )

        # --- Step 2: Summarize with LLM ---
        summary = self._summarize_news(entity, raw_articles)

        # --- Step 3: Extract structured signals with LLM ---
        signals, catalysts, risks = self._extract_signals(entity, raw_articles, summary)

        # --- Step 4: Calculate confidence ---
        confidence = self._calculate_confidence(raw_articles, signals)

        sources = list({a.get("source", "unknown") for a in raw_articles})

        logger.info(f"Business Agent complete for {entity} — confidence: {confidence:.2f}")

        return self._build_output(
            entity=entity,
            timestamp=timestamp,
            signals=signals,
            summary=summary,
            catalysts=catalysts,
            risks=risks,
            confidence=confidence,
            status="complete",
            sources=sources,
            articles=raw_articles,
        )

    # ------------------------------------------------------------------ #
    #  FETCHING
    # ------------------------------------------------------------------ #

    def _fetch_news(self, entity: str, ticker: Optional[str]) -> list[dict]:
        """Fetch news articles from multiple sources."""
        articles = []
        query = ticker or entity

        # Try Google News RSS (most reliable for general entities)
        try:
            rss_url = self.news_sources["general"].format(query=query.replace(" ", "+"))
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:10]:  # Top 10
                articles.append(
                    {
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "source": self._extract_source(entry.get("link", "")),
                        "summary": entry.get("summary", "")[:500],
                    }
                )
        except Exception as e:
            logger.warning(f"RSS fetch failed for {entity}: {e}")

        # Try crypto-specific if entity looks like a crypto project
        if self._is_crypto(entity, ticker):
            try:
                feed = feedparser.parse(self.news_sources["crypto"])
                for entry in feed.entries[:5]:
                    if entity.lower() in entry.title.lower():
                        articles.append(
                            {
                                "title": entry.get("title", ""),
                                "link": entry.get("link", ""),
                                "published": entry.get("published", ""),
                                "source": "cointelegraph",
                                "summary": entry.get("summary", "")[:500],
                            }
                        )
            except Exception as e:
                logger.warning(f"Crypto RSS fetch failed for {entity}: {e}")

        # Deduplicate by title
        seen = set()
        unique = []
        for a in articles:
            if a["title"] not in seen:
                seen.add(a["title"])
                unique.append(a)

        return unique

    def _extract_source(self, url: str) -> str:
        """Extract domain name from URL as source."""
        try:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc
            return domain.replace("www.", "").split(".")[0]
        except Exception:
            return "unknown"

    def _is_crypto(self, entity: str, ticker: Optional[str]) -> bool:
        """Heuristic to detect if entity is a crypto project."""
        crypto_keywords = ["bitcoin", "ethereum", "solana", "crypto", "blockchain", "defi", "token"]
        text = f"{entity} {ticker or ''}".lower()
        return any(k in text for k in crypto_keywords)

    # ------------------------------------------------------------------ #
    #  LLM PROCESSING
    # ------------------------------------------------------------------ #

    def _summarize_news(self, entity: str, articles: list[dict]) -> str:
        """Use Ollama to summarize news articles."""
        if not articles:
            return "No news available."

        # Build prompt
        titles = "\n".join([f"- {a['title']}" for a in articles[:8]])
        prompt = f"""You are a business analyst. Summarize the following news about {entity} in 3-4 sentences. Focus on business developments, partnerships, product launches, and strategic moves. Be factual and concise.

News headlines:
{titles}

Summary:"""

        try:
            response = self.ollama.generate(prompt, model="qwen2.5:7b")
            return response.strip()
        except Exception as e:
            logger.error(f"LLM summary failed: {e}")
            return "Summary generation failed due to LLM error."

    def _extract_signals(self, entity: str, articles: list[dict], summary: str) -> tuple:
        """Use Ollama to extract structured business signals."""
        if not articles:
            return [], [], []

        titles = "\n".join([f"- {a['title']}" for a in articles[:8]])

        prompt = f"""You are an investment research analyst. Analyze the following news about {entity} and extract structured signals.

News:
{titles}

Summary: {summary}

Respond ONLY with valid JSON in this exact format:
{{
  "signals": [
    {{"type": "positive|negative|neutral", "category": "partnership|product|regulation|funding|competition|market", "description": "brief description"}}
  ],
  "catalysts": [
    "upcoming event or recent development that could impact value"
  ],
  "risks": [
    "specific business risk mentioned in news"
  ]
}}

JSON response:"""

        try:
            response = self.ollama.generate(prompt, model="qwen2.5:7b")
            # Clean up response — sometimes LLM adds markdown
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
            return (
                data.get("signals", []),
                data.get("catalysts", []),
                data.get("risks", []),
            )
        except json.JSONDecodeError as e:
            logger.error(f"LLM returned invalid JSON: {e}\nResponse: {response[:200]}")
            return [], [], []
        except Exception as e:
            logger.error(f"Signal extraction failed: {e}")
            return [], [], []

    # ------------------------------------------------------------------ #
    #  CONFIDENCE
    # ------------------------------------------------------------------ #

    def _calculate_confidence(self, articles: list[dict], signals: list[dict]) -> float:
        """Calculate auditable confidence score."""
        # Component 1: Article count (max 0.4)
        article_score = min(len(articles) / 10, 1.0) * 0.4

        # Component 2: Signal richness (max 0.3)
        signal_score = min(len(signals) / 5, 1.0) * 0.3

        # Component 3: Recency (max 0.2) — simplified, assume recent
        recency_score = 0.15  # RSS usually gives recent news

        # Component 4: Source diversity (max 0.1)
        sources = {a.get("source", "unknown") for a in articles}
        diversity_score = min(len(sources) / 3, 1.0) * 0.1

        total = article_score + signal_score + recency_score + diversity_score
        return round(min(total, 1.0), 4)

    # ------------------------------------------------------------------ #
    #  OUTPUT BUILDER
    # ------------------------------------------------------------------ #

    def _build_output(
        self,
        entity: str,
        timestamp: str,
        signals: list,
        summary: str,
        catalysts: list,
        risks: list,
        confidence: float,
        status: str,
        sources: list,
        articles: list,
    ) -> dict:
        """Build standardized agent output dict."""
        return {
            "agent": "business",
            "entity": entity,
            "timestamp": timestamp,
            "metrics": {
                "signal_count": len(signals),
                "positive_signals": len([s for s in signals if s.get("type") == "positive"]),
                "negative_signals": len([s for s in signals if s.get("type") == "negative"]),
                "catalyst_count": len(catalysts),
                "risk_count": len(risks),
            },
            "signals": signals,
            "catalysts": catalysts,
            "risks": risks,
            "summary": summary,
            "confidence": confidence,
            "status": status,
            "sources": sources,
            "raw_articles": articles[:5],  # Store top 5 for reference
        }