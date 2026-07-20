"""
data/db.py

Database layer for AIRS.

Design decisions:
- SQLite: Zero setup, single file, portable. Perfect for MVP.
- One function per operation: init, save, get. Simple to test.
- JSON columns for flexible data: agent outputs and critic feedback are JSON strings.
  This avoids schema changes when agent outputs evolve.
- UNIQUE constraints prevent duplicate data. Re-fetching same ticker+date overwrites.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

# __file__ is the path to THIS file (db.py).
# Path(__file__).parent is the 'data/' folder.
# Path(__file__).parent.parent is the project root (AIRS/).
# We put the database in the project root so it's easy to find.
DB_PATH = Path(__file__).parent.parent / "airs.db"


def get_connection():
    """
    Returns a connection to the SQLite database.
    
    Why a separate function?
    - Every other function uses the same path.
    - If we change DB_PATH later, we only change it here.
    - We can add connection settings (timeouts, row factories) in one place.
    """
    conn = sqlite3.connect(DB_PATH)
    
    # This lets us access columns by name instead of index.
    # Without it: row[0] = id, row[1] = ticker (hard to read, easy to break)
    # With it: row["id"], row["ticker"] (self-documenting)
    conn.row_factory = sqlite3.Row
    
    return conn


def init_db():
    """
    Creates the database and all tables if they don't exist.
    
    SQLite has a quirk: INTEGER PRIMARY KEY auto-increments even without AUTOINCREMENT.
    We use AUTOINCREMENT anyway to be explicit and prevent ID reuse after deletes.
    
    We use TEXT for dates because SQLite has no native date type.
    ISO format (YYYY-MM-DD) sorts correctly as text, so it's fine.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # --- market_data table ---
    # Stores OHLCV (Open, High, Low, Close, Volume) price data.
    # UNIQUE(ticker, date) prevents the same price being stored twice.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, date)
        )
    """)
    
    # Index: makes "get all AAPL data" queries fast.
    # Without it, SQLite scans every row. With 10k rows, that's slow.
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_market_ticker_date 
        ON market_data(ticker, date)
    """)
    
    # --- entities table ---
    # Stores what we're analyzing: companies, crypto, AI projects.
    # type: "stock", "crypto", "ai_company"
    # github_repo: optional, format "owner/repo"
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ticker TEXT,
            type TEXT NOT NULL,
            github_repo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # --- research_states table ---
    # Tracks where we are in the loop.
    # agent_outputs and critic_feedback are JSON strings.
    # This is flexible: if we add a new agent, we don't need to alter schema.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL,
            iteration INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'planning',
            agent_outputs TEXT,
            critic_feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entity_id) REFERENCES entities(id)
        )
    """)
    
    # --- reports table ---
    # Final output: the investment memo.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL,
            report_text TEXT,
            confidence REAL,
            iteration_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entity_id) REFERENCES entities(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")


def save_market_data(ticker: str, df):
    """
    Saves a pandas DataFrame of stock data to the database.
    
    Args:
        ticker: Stock symbol, e.g. "AAPL"
        df: pandas DataFrame with DatetimeIndex and columns [Open, High, Low, Close, Volume]
    
    Why 'INSERT OR REPLACE'?
    - If we run the script twice for the same ticker, we don't crash.
    - We overwrite old data with new data. This is called "upsert."
    
    Why use .iterrows()?
    - pandas DataFrames are row-based. We iterate once and insert each row.
    - For 1000 rows, this is fine. For 1M rows, we'd use df.to_sql() instead.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    count = 0
    for date, row in df.iterrows():
        # date is a pandas Timestamp. Convert to string for SQLite.
        date_str = date.strftime("%Y-%m-%d")
        
        cursor.execute("""
            INSERT OR REPLACE INTO market_data 
            (ticker, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker,
            date_str,
            float(row["Open"]),
            float(row["High"]),
            float(row["Low"]),
            float(row["Close"]),
            int(row["Volume"])
        ))
        count += 1
    
    conn.commit()
    conn.close()
    print(f"Saved {count} rows for {ticker}")


def get_market_data(ticker: str, limit: int = 30):
    """
    Retrieves market data for a ticker, newest first.
    
    Args:
        ticker: Stock symbol
        limit: Max rows to return (default 30 = last 30 days)
    
    Returns:
        List of dicts, each dict is one row. Newest first.
    
    Why list of dicts?
    - Easy to convert to JSON (for APIs)
    - Easy to iterate in loops
    - Self-documenting: row["close"] is clearer than row[4]
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM market_data 
        WHERE ticker = ?
        ORDER BY date DESC
        LIMIT ?
    """, (ticker, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert sqlite3.Row objects to plain dicts
    # This is called "serialization" — database rows → Python objects
    return [dict(row) for row in rows]


def save_entity(name: str, ticker: str = None, type_: str = "stock", github_repo: str = None) -> int:
    """
    Saves an entity and returns its ID.
    
    Args:
        name: Display name, e.g. "NVIDIA"
        ticker: Symbol, e.g. "NVDA"
        type_: "stock", "crypto", or "ai_company"
        github_repo: Optional, e.g. "NVIDIA/open-gpu-kernel-modules"
    
    Returns:
        The entity's ID (integer)
    
    Why return the ID?
    - Other functions need entity_id as a foreign key.
    - This lets us link research_states and reports to the right entity.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO entities (name, ticker, type, github_repo)
        VALUES (?, ?, ?, ?)
    """, (name, ticker, type_, github_repo))
    
    entity_id = cursor.lastrowid  # SQLite tells us the new row's ID
    conn.commit()
    conn.close()
    
    return entity_id


def get_entity(name: str):
    """
    Finds an entity by name.
    
    Returns:
        Dict with entity data, or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM entities WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def save_research_state(entity_id: int, iteration: int, status: str, 
                        agent_outputs: dict = None, critic_feedback: dict = None):
    """
    Saves the current state of the research loop.
    
    Args:
        entity_id: FK to entities table
        iteration: Which loop iteration (1, 2, 3)
        status: "planning", "researching", "analyzing", "critiquing", "complete"
        agent_outputs: Dict of all agent results (serialized to JSON)
        critic_feedback: Dict of critic evaluation (serialized to JSON)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # json.dumps converts Python dict to JSON string for SQLite storage
    cursor.execute("""
        INSERT INTO research_states 
        (entity_id, iteration, status, agent_outputs, critic_feedback)
        VALUES (?, ?, ?, ?, ?)
    """, (
        entity_id,
        iteration,
        status,
        json.dumps(agent_outputs) if agent_outputs else None,
        json.dumps(critic_feedback) if critic_feedback else None
    ))
    
    conn.commit()
    conn.close()


def get_latest_research_state(entity_id: int):
    """
    Gets the most recent research state for an entity.
    
    Returns:
        Dict, or None if no research exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM research_states 
        WHERE entity_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (entity_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    result = dict(row)
    # json.loads converts JSON string back to Python dict
    if result.get("agent_outputs"):
        result["agent_outputs"] = json.loads(result["agent_outputs"])
    if result.get("critic_feedback"):
        result["critic_feedback"] = json.loads(result["critic_feedback"])
    
    return result