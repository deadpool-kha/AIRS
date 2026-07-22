
---

# CHANGELOG.md

# Project History

## [0.1.0] - 2026-07-19

### Added
- `MEMORY.md` — Project context and architecture overview
- `ROADMAP.md` — Phase-based development plan
- `ARCHITECTURE.md` — System architecture with loop engineering
- `DECISIONS.md` — Engineering decision log (5 initial decisions)
- `SPEC.md` — Product specification with functional requirements
- `SETUP.md` — Developer onboarding guide
- `CURRENT_TASK.md` — Development status tracker
- `LEARNING.md` — Knowledge capture log
- `CHANGELOG.md` — This file

### Decisions
- Python as primary language
- Local LLMs (Ollama) instead of paid APIs
- SQLite for database
- Focused investment research workflow (not generic chatbot)
- Controlled agent loops (loop engineering)

---

## [0.2.0] - 2026-07-20

### Added
- Loop engineering architecture (Critic Agent, iteration control)
- 4-agent design (Quant, Technical, Business, Risk)
- Error handling strategy
- Data models specification (Agent, Critic, Loop State)
- Git workflow documentation

### Updated
- `MEMORY.md` — Added loop engineering, 4-agent design, Git workflow
- `ARCHITECTURE.md` — Added Critic Agent, error handling, LLM layer details
- `ROADMAP.md` — Changed from day-based to phase-based with Definition of Done
- `CURRENT_TASK.md` — Added issue tracking, priority ordering
- `DECISIONS.md` — Added Decisions 005, 006, 007
- `SPEC.md` — Added FR-005 (Research Loop), data models, error handling
- `CHANGELOG.md` — Added v0.2.0 entry
- `LEARNING.md` — Added 4 knowledge entries
- `SETUP.md` — Added verify installation, .gitignore, troubleshooting
- `requirements.txt` — Added yfinance, ollama, jinja2, PyGithub, pytest, feedparser

---

## [0.3.0] - 2026-07-20

### Added
- `setup_project.py` — Automated project scaffold script
- `data/db.py` — SQLite database with 4 tables (market_data, entities, research_states, reports)
- `data/fetcher.py` — Yahoo Finance wrapper with exponential backoff retry
- `agents/quant.py` — Quant Agent with full financial metrics:
  - Returns (daily, weekly, monthly)
  - Volatility (annualized)
  - Momentum (5d, 10d, 20d, 30d)
  - Moving averages (SMA 10, 20, 50)
  - Drawdown (max with peak/trough dates)
  - Risk score (composite 0-1)
  - Trend detection (bullish/bearish)
- `main.py` — CLI entry point with `--entity` and `--quant-only` flags


---

## [0.3.1] - 2026-07-21

### Added
- Auditable confidence system based on DDScore feedback (Issue #13)
  - Confidence breakdown: data sufficiency (30%), metric completeness (30%), data freshness (20%), calculation stability (20%)
  - Each metric includes source tracking: source, ticker, period, calculation method, timestamp
  - `--show-sources` CLI flag to display full traceability
  - Default output stays clean; detailed view available on demand
- `critic_history` table in SQLite for append-only feedback tracking

### Changed
- `agents/quant.py`: Confidence now calculated from components, not just row count
- `main.py`: Added `--show-sources` argument, conditional source display

### External Feedback
- Issue #13: DDScore (Playful Pixels Oy) provided detailed feedback on confidence auditability
- Response: Implemented lightweight version of MemoClaimReceipt principles for MVP

### Closed Issues
- #4: Implement Quant Agent (enhanced with v2 features)

### Verified
- AAPL data fetches and persists correctly
- Quant Agent produces structured analysis output
- Database stores and retrieves data across script runs

### Decisions
- Use `INSERT OR REPLACE` for idempotent data storage
- Use `json.dumps` for flexible agent output columns
- Use exponential backoff (1s, 2s, 4s) for API retries
- Separate fetcher from database (Adapter Pattern)

### Closed Issues
- #1: Initialize Python project structure
- #2: Create database foundation
- #3: Build first market data collector
- #4: Implement Quant Agent