"""
config/sectors.py

Sector canonicalization system for AIRS.

Design decisions:
- Explicit assignment only. No auto-detection (would require LLM or external API).
- Kebab-case canonical names (lowercase with hyphens).
- Fuzzy matching + aliases for user convenience.
- Strict validation: unknown sectors = ERROR, not silent NULL.
"""

import difflib


CANONICAL_SECTORS = {
    "semiconductors",
    "consumer-tech",
    "enterprise-software",
    "cybersecurity",
    "saas",
    "cloud-infrastructure",
    "generative-ai",
    "ai-infrastructure",
    "data-analytics",
    "e-commerce",
    "streaming",
    "mobility",
    "database",
    "l1-blockchain",
    "backend-as-a-service",
    "frontend-infrastructure",
    "ev-energy",
}

SECTOR_ALIASES = {
    "semi": "semiconductors",
    "semiconductor": "semiconductors",
    "chip": "semiconductors",
    "ai": "generative-ai",
    "gen-ai": "generative-ai",
    "cloud": "cloud-infrastructure",
    "security": "cybersecurity",
    "crypto": "l1-blockchain",
    "blockchain": "l1-blockchain",
    "web3": "l1-blockchain",
    "software": "enterprise-software",
    "social": "consumer-tech",
    "retail": "e-commerce",
    "auto": "ev-energy",
    "car": "ev-energy",
    "video": "streaming",
    "music": "streaming",
}


def normalize_sector(user_input):
    """
    Normalize user-provided sector to canonical form.
    
    Args:
        user_input: Raw sector string from CLI or config.
    
    Returns:
        Canonical sector name (str) or None if unresolvable.
    """
    if not user_input:
        return None
    
    cleaned = user_input.strip().lower().replace(" ", "-").replace("_", "-")
    
    # Exact match
    if cleaned in CANONICAL_SECTORS:
        return cleaned
    
    # Alias match
    if cleaned in SECTOR_ALIASES:
        return SECTOR_ALIASES[cleaned]
    
    # Fuzzy match (Levenshtein distance, 80% similarity cutoff)
    all_options = list(CANONICAL_SECTORS) + list(SECTOR_ALIASES.keys())
    matches = difflib.get_close_matches(cleaned, all_options, n=1, cutoff=0.8)
    if matches:
        matched = matches[0]
        if matched in SECTOR_ALIASES:
            return SECTOR_ALIASES[matched]
        return matched
    
    return None


def list_sectors():
    """
    Return sorted list of canonical sectors.
    
    Returns:
        List of canonical sector strings.
    """
    return sorted(CANONICAL_SECTORS)


def validate_watchlist_sectors(watchlist_data):
    """
    Validate all sectors in watchlist JSON are canonical.
    
    Args:
        watchlist_data: Parsed JSON dict from config/watchlist.json
    
    Raises:
        ValueError: If any sector is not canonical.
    """
    invalid = []
    for category, entities in watchlist_data.get("watchlists", {}).items():
        for item in entities:
            sector = item.get("sector")
            if sector and normalize_sector(sector) != sector:
                invalid.append(
                    f"Category '{category}', entity '{item.get('entity', '?')}': "
                    f"invalid sector '{sector}'"
                )
    
    if invalid:
        raise ValueError(
            "Watchlist contains invalid sectors:\n  " + "\n  ".join(invalid) +
            "\nRun 'python main.py --list-sectors' to see valid options."
        )