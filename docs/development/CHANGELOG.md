
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

## [0.3.2] - 2026-07-21

### Added
- Technical Agent for GitHub ecosystem analysis
  - Fetches commits, repo metadata, contributors from GitHub REST API
  - Calculates commit frequency (commits per week)
  - Calculates days since last commit
  - Composite health score (0-1) based on 4 factors
  - Graceful handling of rate limits and missing data
- Combined mode: run Quant + Technical together
- `--technical-only` CLI flag
- `--repo` argument for GitHub repository input

### Changed
- `main.py`: argparse refactored — `--entity` not required when using `--technical-only`
- `agents/technical.py`: New agent module

### Technical Details
- Uses `requests` library directly instead of PyGithub
- Unauthenticated API calls (60/hr limit)
- JSON response parsing with error handling

### Closed Issues
- #5: Implement Technical Agent

---

## [0.3.3] - 2026-07-23

### Added
- Business Agent (`agents/business.py`) — Issue #6
  - RSS news fetching (Google News, CoinTelegraph for crypto)
  - Ollama LLM summarization (qwen2.5:7b)
  - Structured signal extraction (positive/negative/neutral, category, description)
  - Catalyst and risk identification
  - Auditable confidence with 4 components (article count, signal richness, recency, source diversity)
  - `--business-only` CLI flag
  - `--ticker` argument for better news matching
- Risk Agent (`agents/risk.py`) — Issue #7
  - Rules-based downside analysis (no LLM, deterministic)
  - Cross-agent contradiction detection (e.g., strong quant + weak technical)
  - Blind spot detection (all-positive signal warning)
  - Severity classification (high/medium)
  - `--risk-only` CLI flag (redirects to --hypotheses)
- Hypothesis Competition Engine (`reports/hypothesis.py`) — Issue #10 (partial)
  - Bull/bear/base case generation from agent outputs
  - Evidence collection per hypothesis
  - Probability normalization with 5% minimum floor (DDScore #13 compliance)
  - `--hypotheses` CLI flag integration
- `utils/ollama_client.py` — Ollama API wrapper with retry logic

### Changed
- `main.py`: Refactored to support 4 agents + hypothesis mode
- `main.py`: Added `--business-only`, `--ticker`, `--hypotheses`, `--risk-only` flags
- Hypothesis engine now consumes Business Agent and Risk Agent outputs

### Technical Details
- Business Agent: 2 LLM calls per run (summarize + extract), ~60-90s on GTX 1060
- Risk Agent: Pure Python, &lt;1s execution
- Ollama timeout: 60s default, exponential backoff retry (1s, 2s, 4s)

### Closed Issues
- #6: Implement Business Agent
- #7: Implement Risk Agent

### Decisions
- Business Agent uses RSS + Ollama (local, $0 cost) — aligns with Decision #002
- Risk Agent is rules-based (no LLM) — aligns with architecture principle: deterministic analysis without LLM dependency
- Hypothesis minimum probability floor (5%) — DDScore #13 feedback implementation

### Verified
- AAPL: Full pipeline runs end-to-end (Quant → Technical → Business → Risk → Hypotheses)
- NVIDIA: Business Agent produces structured signals, catalysts, risks
- apple/swift: Technical Agent health score 0.7, commit frequency 350/week
- Hypothesis output: Bull 41% / Bear 18% / Base 41% for AAPL (with Risk Agent input)


---






## [0.3.4] - 2026-07-26

### Added
- Critic Agent (`agents/critic.py`) — Issue #8
  - Rule-based research quality evaluation across all 4 agents
  - Cross-agent validation: confidence-risk mismatch detection
  - NEW: Mandatory iteration trigger when Risk Agent flags HIGH risk
  - NEW: Business signal bias detection (all-positive warning)
  - LLM-enhanced suggestions via Ollama when gaps found
  - `--critic` CLI flag (integrated into `--hypotheses` mode)
  - Append-only findings (Decision #012 compliance)

### Changed
- `reports/hypothesis.py`: Risk Agent output now feeds into bear case evidence
  - Individual risks add +5% probability each
  - Warnings add +3% probability each
  - HIGH overall risk flag adds +15% probability
  - Bear case now reflects real risks (25% vs artificial 5% for AAPL)
- `agents/critic.py`: Quality score calculation includes warnings metric
- `main.py`: `--hypotheses` mode now runs Critic Agent before hypothesis generation

### Fixed
- Critic no longer reports "complete" when Risk Agent flags HIGH risk
- Bear case no longer shows 5% minimum floor with empty evidence
- Cross-agent gap detection now triggers `should_iterate = True`

### Technical Details
- Critic: 8 quality checks (quant, technical, business, risk, cross-agent, dimensions)
- LLM suggestions: 30s timeout, skipped if rule-based already complete
- Hypothesis re-normalization: floor applied, then re-normalized to sum 1.0

### Closed Issues
- #8: Implement Critic Agent

### Decisions
- Critic uses rule-based + optional LLM enhancement — aligns with architecture principle: deterministic base, LLM for reasoning only
- HIGH risk mandates iteration — DDScore #13: "unknowns remain unknown" until investigated
- Business bias warning — prevents confirmation bias in news analysis

### Verified
- AAPL: Critic flags `high_risk_not_mitigated`, triggers iteration
- AAPL: Bear case 25% with 3 risk evidence items
- AAPL: LLM suggests "scenario analysis and stress testing"
- AAPL: Quality score 0.875 (partial), should_iterate = True

---

## [0.3.5] - 2026-07-26

### Fixed
- `agents/quant.py`: Timezone bug — `pd.Timestamp.now()` failed on tz-naive dataframes
  - Now handles both tz-aware and tz-naive datetime objects
- `agents/technical.py`: Typo `status_status_code` → `status_code`
  - Was causing AttributeError on API error responses
  - Now returns clean 404 errors instead of crashing

### Verified
- ORCL: Quant Agent runs without timezone crash
- ORCL: Technical Agent returns clean 404 instead of traceback

## [2026-07-30] Issue #9: Loop Controller

### Added
- Created `controller/loop.py` with:
  - Loop Controller supporting a maximum of **3 iterations**
  - Database persistence
  - Graceful agent skipping
- Added `loop_states` table in `data/db.py` to track:
  - Iteration history
  - Critique summaries
- Added `"skipped"` status handling in `agents/critic.py` for intentionally missing agents (no repository or no ticker).
- `--hypotheses` no longer requires `--repo` and now supports partial agent sets (e.g., Quant + Business only).

### Changed
- Updated `main.py` so the `--hypotheses` workflow is orchestrated through `LoopController` instead of inline orchestration.
- Updated `agents/critic.py` with iteration-aware evaluation and automatic `high_risk_not_mitigated` triggering.
- Updated `main.py` validation so `--hypotheses` no longer enforces the `--repo` argument.

### Fixed
- Fixed an `AttributeError` that occurred when `--repo` was omitted in `--hypotheses` mode.
- Fixed Critic incorrectly reporting intentionally skipped agents as `technical_no_data` gaps.
- Fixed loop termination logic so execution correctly stops on iteration 3 when the Critic is satisfied (corrected max-iteration check ordering).

### Known Issues
- Business Agent iterations 2 and 3 reuse the same RSS feeds (live feeds only; no historical access).
- Technical Agent iterations 2 and 3 reuse the same GitHub repository snapshot (repository state is unchanged).
- Only the Quant Agent currently benefits from updated inputs between iterations.


---



```markdown
## [0.3.6] - 2026-07-31

### Added
- `core/evidence.py` — Evidence Register with provenance tracking (source, tier, data_points, data_period, timestamp)
- Critic Agent v2 — 6-phase analyst model:
  - Phase 1: Inventory
  - Phase 2: Directional Signals (bullish/bearish/neutral per dimension)
  - Phase 3: Dashboard (Data Quality, Coverage, Agreement, Stability)
  - Phase 4: Contradictions (12 hardcoded rules + catch-all)
  - Phase 5: Active Questions (specific research questions, not feature checklists)
  - Phase 6: Halt Decision (iteration-aware: coherent view / stable thesis / circuit breaker)
- Dashboard-driven halt logic — loop stops when view is coherent, not when checklist is full
- Hypothesis Engine v3 — evidence-weighted directional bias + explicit uncertainty:
  - `directional_bias`: Bullish strength vs Bearish strength (raw scores)
  - `uncertainty`: Separate score (Scarcity + Conflict + Coverage)
  - `claims`: Structured evidence with source, raw_value, strength, direction
  - Base case = neutral signals, not "leftover probability"
- Stability tracking — Critic compares current vs previous iteration dashboard
- Active Questions — each question includes "Why it matters" and whether deeper data can resolve it
- `dashboard_history` column in `loop_states` SQLite table

### Changed
- `agents/critic.py` — Complete rewrite. Old checklist-based audit replaced with phased analyst model.
- `reports/hypothesis.py` — Killed fake probability percentages. No more 5% floor. No more three-way 100% normalization.
- `controller/loop.py` — Passes `previous_critic_output` for stability tracking. Displays dashboard instead of flat confidence.
- `main.py` — Final summary renders Dashboard, Directional Bias, Uncertainty, Active Questions, Unresolved Contradictions.
- Loop behavior: Business and Technical run once (bootstrap). Only Quant iterates. Loop halts early when view is coherent.

### Removed
- "Confidence: 100%" flat score — replaced with 4-dimensional dashboard
- `missing_evidence` as primary loop driver — replaced with Active Questions
- 5% minimum probability floor in hypotheses — superseded by explicit uncertainty metric

### Fixed
- Treadmill loop eliminated — old system ran all agents 3× with same inputs; new system halts at iteration 1 when dimensions agree
- Fake probabilities eliminated — old system produced Bear 49% / Base 43% / Bull 7% from heuristic point-scoring; new system produces directional bias + uncertainty

### Tested
- AAPL: Halted at iteration 1 (not 3). Dashboard: Data Quality 81%, Coverage 59%, Agreement High, Stability Unknown. Directional Bias: BEARISH (Bull 0.58, Bear 1.68, Net -1.10). Uncertainty: Moderate 29%.

### Decisions
- Decision 027: Kill fake probability percentages — directional bias + uncertainty
- Decision 028: Critic as analyst (iteration-aware) not auditor (checklist)
- Decision 029: Uncertainty as separate dimension from directional conviction
- Decision 030: Dashboard-driven halt logic
- Decision 031: Evidence Register as single source of truth
- Decision 017 deprecated: 5% floor was mathematically dishonest

### Known Issues
- Risk Agent still reads legacy `agent_outputs` dict via bridge; does not read directly from Evidence Register yet
- Hypothesis strength thresholds (0.35, 0.45, 0.60, 0.75) are intuitive, not validated against historical data
- Agreement logic treats "mixed signals" neutral the same as "missing data" neutral; could be tightened


## [0.3.7] - 2026-08-05

### Added
- `reports/generator.py` — Issue #10: Professional investment memo generator
  - Jinja2-templated Markdown reports with 7 sections:
    - Executive Summary, Audit Dashboard, Investment Thesis, Evidence Register Summary,
      Risk Assessment, Active Questions & Unresolved Contradictions, Appendix
  - Optional PDF export via `--pdf` flag (requires weasyprint; graceful fallback if missing)
  - `reports/templates/report.md.j2` — clean separation of logic and presentation
- Report auto-generated at end of `--hypotheses` workflow
- Report output attached to loop `results` dict for programmatic access

### Changed
- `controller/loop.py` — Integrated `generate_report()` into `_final_output()`
- `main.py` — Added `--pdf` CLI flag; updated banner to v0.3.7

### Verified
- AAPL: Full 3-iteration loop with all dimensions (Quant + Business + Technical)
- Report correctly renders: raw quant metrics, business signals, technical health scores
- PDF gracefully skips when weasyprint unavailable