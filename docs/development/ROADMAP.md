# ROADMAP.md

# Project: Autonomous Investment Research System (AIRS)

## Timeline

Target completion: 3-4 weeks

Primary goal:

Build a portfolio-quality AI engineering system demonstrating:

* agent architecture
* loop engineering
* data pipelines
* quantitative analysis
* LLM integration
* backend engineering

Secondary goal:

Create a project that can be shown to:

* AI startups
* fintech companies
* crypto companies
* data companies
* research/quant teams

---

# Development Philosophy

Build a working system first.

Avoid:

* unnecessary complexity
* perfect UI
* excessive agent count
* paid APIs
* premature deployment

The priority:

Working system &gt; beautiful interface &gt; advanced features

---

# Phase 0: Setup

## Goal: Project foundation exists

### Definition of Done:
- [x] GitHub repository initialized
- [x] Python virtual environment created
- [x] Folder structure created
- [x] README.md with project overview
- [x] requirements.txt with pinned dependencies
- [x] .gitignore configured
- [x] All documentation files (.md) in place
- [x] First commit pushed

### Estimated: 1-2 days
### Blocked by: Nothing
### Blocks: Phase 1

---

# Phase 1: Data Foundation

## Goal: System can collect and store market data

### Definition of Done:
- [x] SQLite schema created and tested
- [x] market_data table with proper indexes
- [x] entities table
- [x] research_states table (for loop tracking)
- [x] loop_states table (for iteration history and dashboard snapshots)
- [x] yfinance fetcher working (AAPL, BTC-USD)
- [x] Data persists across script runs
- [x] Error handling for API failures
- [x] Unit tests for fetcher and db modules

### Estimated: 3-5 days
### Blocked by: Phase 0
### Blocks: Phase 2

---

# Phase 2: Quant Agent

## Goal: System produces quantitative analysis

### Definition of Done:
- [x] Calculate returns (daily, weekly, monthly)
- [x] Calculate volatility (standard deviation)
- [x] Calculate momentum (rate of change)
- [x] Calculate drawdown (max peak-to-trough)
- [x] Calculate risk score
- [x] Calculate RSI, MACD, volume profile
- [x] Tiered computation: Tier 1 (3mo), Tier 2 (6mo), Tier 3 (1y)
- [x] Output structured dict with confidence breakdown
- [x] No LLM used — pure Python/pandas
- [x] Unit tests

### Estimated: 2-3 days
### Blocked by: Phase 1
### Blocks: Phase 5, 6, 7

---

# Phase 3: Technical Agent

## Goal: System evaluates technical ecosystem health

### Definition of Done:
- [x] GitHub API integration (unauthenticated)
- [x] Fetch commits, contributors, issues, releases
- [x] Calculate contributor growth rate
- [x] Calculate commit frequency
- [x] Assess project maintenance health
- [x] Output structured dict
- [x] Handle rate limits gracefully

### Estimated: 3-4 days
### Blocked by: Phase 1
### Blocks: Phase 5, 6, 7

---

# Phase 4: Business Agent

## Goal: System understands qualitative information

### Definition of Done:
- [x] RSS/news fetching capability
- [x] Local LLM (Ollama) summarization
- [x] Extract catalysts and events
- [x] Structured signal extraction (positive/negative/neutral)
- [x] Output structured dict with sources
- [x] Fallback when no news found

### Estimated: 2-3 days
### Blocked by: Phase 1
### Blocks: Phase 5, 6, 7

---

# Phase 5: Risk Agent

## Goal: System identifies downside and weaknesses

### Definition of Done:
- [x] Analyze negative signals from all agents
- [x] Identify competition and regulatory risks
- [x] Assess concentration and volatility risks
- [x] Output structured risk assessment
- [x] Uses rules-based analysis (no LLM)
- [x] Cross-agent contradiction detection
- [x] Blind-spot warnings

### Estimated: 2-3 days
### Blocked by: Phase 2, 3, 4
### Blocks: Phase 6, 7

---

# Phase 6: Critic Agent

## Goal: System evaluates research quality and directs inquiry

### Definition of Done:
- [x] 6-phase analyst model implemented:
  - Phase 1: Inventory
  - Phase 2: Directional Signals
  - Phase 3: Dashboard (Data Quality, Coverage, Agreement, Stability)
  - Phase 4: Contradictions (12 hardcoded rules + catch-all)
  - Phase 5: Active Questions
  - Phase 6: Halt Decision (iteration-aware)
- [x] 100% rule-based — no LLM decides halt
- [x] Dashboard-driven evaluation
- [x] Cross-agent validation
- [x] Optional LLM suggestions (display-only, non-binding)

### Estimated: 3-4 days
### Blocked by: Phase 2, 3, 4, 5
### Blocks: Phase 7

---

# Phase 7: Loop Controller

## Goal: System iterates and improves research quality adaptively

### Definition of Done:
- [x] Loop controller implemented with bootstrap pattern
- [x] Business + Technical agents run once per session
- [x] Quant Agent iterates with tiered data depth (Tier 1 → Tier 2 → Tier 3)
- [x] Critic receives previous output for stability tracking
- [x] Dashboard history persisted to SQLite
- [x] Early halt when view is coherent (not always 3 iterations)
- [x] Max 3 iterations enforced as circuit breaker
- [x] Evidence Register as single source of truth
- [x] Hypothesis Engine v3: Directional Bias + Uncertainty (no fake probabilities)

### Includes: Issue #9b+ — Evidence-Driven Loop Evolution
- [x] Evidence Register with provenance tracking
- [x] Critic redesign: analyst model replacing checklist auditor
- [x] Hypothesis redesign: directional bias + uncertainty replacing probability normalization
- [x] Dashboard-driven halt logic
- [x] Active Questions replacing missing_evidence checklists

### Estimated: 3-4 days
### Blocked by: Phase 2, 3, 4, 5, 6
### Blocks: Phase 8

---

# Phase 8: Report Generator

## Goal: System generates professional investment memo

### Definition of Done:
- [x] Combine dashboard, hypotheses, active questions, and contradictions
- [x] Jinja2-templated Markdown reports (no LLM for table formatting)
- [x] Markdown output with 7 sections:
  - Executive Summary
  - Audit Dashboard
  - Investment Thesis (Directional Bias + Uncertainty)
  - Evidence Register Summary
  - Risk Assessment
  - Active Questions & Unresolved Contradictions
  - Appendix
- [x] Cites evidence and sources
- [x] Handles partial data gracefully
- [x] `reports/generator.py` with `ReportGenerator` class
- [x] Optional PDF export via WeasyPrint (graceful fallback)
- [x] Reports saved to `reports/output/` subdirectory
- [x] CLI `--pdf` flag support

### Status: ✅ Complete (Issue #10)
### Branch: `feature/#10-report-generator`
### Estimated: 2-3 days
### Blocked by: Phase 7
### Blocks: Phase 9, 10

---

# Phase 9: Audit Trail & Backtesting

## Goal: System learns from its own predictions

### Definition of Done:
- [x] `research_sessions` table: entity, asset_type, date, dashboard, halt_reason, sector, evidence_snapshot
- [x] `research_outcomes` table: session_id, actual_direction, price_change_30d, accuracy_score
- [x] Save full Evidence Register snapshot per session (JSON blob with numpy-safe serialization)
- [x] Save hypotheses (directional_bias + uncertainty) per session
- [x] CLI command to query historical accuracy: `python main.py --audit`
- [x] Batch watchlist runner: `python main.py --watchlist all --hypotheses`
- [x] Sector tagging with strict validation
- [ ] 30-day outcome scoring (time-gated — requires sessions to age)

### Status: ✅ Infrastructure Complete (Issue #12)
### Branch: `feature/#12-audit-trail`
### Estimated: 2-3 days
### Blocked by: Phase 8
### Blocks: Phase 9.5

---

# Phase 9.5: Audit Trail Polish

## Goal: Richer analysis once sufficient historical data exists

### Definition of Done:
- [ ] `--audit --export-csv` for external analysis
- [ ] Trend graphs (accuracy over time) once 20+ scored sessions
- [ ] Per-sector accuracy grouping with statistical significance
- [ ] Composite evidence strength (conviction + diversity + depth)
- [ ] Historical session backfill (35 sessions for immediate stats)

### Status: 📅 Planned (pending 30-day aging)
### Estimated: 1-2 days
### Blocked by: Phase 9
### Blocks: Nothing

# Phase 10: Interface and Presentation

## Goal: Project is presentable to non-technical users

### Definition of Done:
- [ ] Streamlit interface for interactive research
- [ ] README with screenshots of dashboard output
- [ ] Updated architecture diagram
- [ ] Demo video or GIF
- [ ] Example reports in repo
- [ ] Deployed or easily runnable

### Status: 📅 Planned
### Estimated: 2-3 days
### Blocked by: Phase 8
### Blocks: Nothing

---



# Minimum Viable Version

If time becomes limited:

Must have:
- [x] Quant Agent
- [x] Technical Agent
- [x] Loop Controller
- [x] Critic Agent
- [x] Evidence Register
- [x] Hypothesis Engine (Directional Bias + Uncertainty)
- [x] Report Generator
- [x] Audit Trail Infrastructure (session persistence, outcome recording, stats)

Optional:
- [ ] 30-Day Outcome Scoring (time-gated, will populate automatically)
- [ ] Streamlit UI
- [ ] Entity Disambiguation

---

# Future Improvements

Not part of MVP:

* **Entity Disambiguation** — Auto-resolve ambiguous names (e.g., "Apple" → AAPL vs private company) via web search + yfinance + CoinGecko matching
* **Real-time monitoring**
* **Portfolio management**
* **Trading execution**
* **Additional agents** (ESG, Macro, On-chain)
* **Cloud deployment**
* **User accounts**
* **Mobile app**

---

# Success Criteria

The project is successful if:

1. A stranger can understand it from GitHub.
2. A user can run an analysis with a single command.
3. The system produces a structured report with an auditable dashboard.
4. The loop demonstrates self-improving, adaptive research (halts early when coherent).
5. Directional bias and uncertainty are explicit and honest.
6. Architecture demonstrates modern AI engineering.
7. The developer can explain every design decision.
8. Every output is traceable to evidence in the Evidence Register.