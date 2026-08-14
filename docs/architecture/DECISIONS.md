# DECISIONS.md

# Engineering Decision Log

This file records important technical decisions and the reasoning behind them.

---

# Decision 001

## Use Python as primary language

Date: 2026-07-19

Decision:

Use Python for backend and AI development.

Reason:

* Strong ecosystem for AI and data science
* Good libraries for finance and ML
* Faster development speed

Rejected alternatives:
* TypeScript/Node.js (less mature for data science)
* Go (faster but less library support for AI)
* Rust (too complex for MVP)

Revisit if: Performance becomes critical at scale

---

# Decision 002

## Use local LLMs instead of paid APIs initially

Date: 2026-07-19

Decision:

Use Ollama with open-source models.

Reason:

* Project budget is $0
* Avoid API token costs
* Demonstrate local AI capability
* Data privacy (no data leaves machine)

Rejected alternatives:
* OpenAI GPT-4 (costs money)
* Anthropic Claude (costs money)
* Google Gemini (free tier has limits)

Revisit if: Local models insufficient for report quality

---

# Decision 003

## Use SQLite initially

Date: 2026-07-19

Decision:

Start with SQLite instead of PostgreSQL.

Reason:

* Zero setup
* Enough for MVP
* Easy local development
* Portable (single file)

Rejected alternatives:
* PostgreSQL (requires installation and configuration)
* MongoDB (overkill for structured data)
* Redis (not persistent enough)

Revisit if: Scale requires concurrent writes or complex queries

---

# Decision 004

## Do not build a generic chatbot

Date: 2026-07-19

Decision:

Focus on investment research workflow.

Reason:

Generic chatbots are common and provide little differentiation.

The value comes from:

* data pipelines
* workflow automation
* analysis quality
* domain application

Rejected alternatives:
* Generic RAG chatbot (too common, not impressive)
* Simple Q&A system (doesn't demonstrate engineering)

---

# Decision 005

## Use controlled agent loops (loop engineering)

Date: 2026-07-20

Decision:

Use a defined research workflow with explicit iteration instead of uncontrolled autonomous agents.

Reason:

Improves:

* reliability
* debugging
* cost control
* evaluation
* transparency



The loop: Plan → Research → Analyze → Critique → (Iterate or Complete)

Rejected alternatives:
* Uncontrolled autonomous agents (unpredictable, hard to debug)
* Single-pass analysis (no quality improvement)
* Pure LLM chain (expensive, unreliable)

Revisit if: Need more autonomous behavior for advanced use cases

---

# Decision 006

## Use 4 specialized agents + 1 critic agent

Date: 2026-07-20

Decision:

Quant, Technical, Business, Risk agents + Critic agent.

Reason:

* Enough complexity to demonstrate multi-agent system
* Each has clear, distinct responsibility
* Feasible to build in 3-4 weeks
* Covers key dimensions of investment research

Rejected alternatives:
* 2 agents (too simple)
* 6+ agents (scope creep, never finish)
* Single monolithic agent (not modular)

Revisit if: Need more specialized analysis (e.g., ESG, macro)

---

# Decision 007

## Use GitHub Issues for all work tracking

Date: 2026-07-20

Decision:

Every task, bug, and feature gets a GitHub issue.

Reason:

* Clear history of decisions and progress
* Easy to reference in commits
* Demonstrates professional workflow
* Helps with portfolio storytelling

Rejected alternatives:
* Trello (external, not tied to code)
* Jira (overkill for solo project)
* Mental tracking (unreliable, not visible)

Revisit if: Project grows to 3+ contributors

---

# Decision 008

## Use INSERT OR REPLACE for idempotent storage

Date: 2026-07-20

Decision:
Use SQLite's INSERT OR REPLACE instead of INSERT.

Reason:
- Prevents crashes when re-fetching same ticker+date
- Makes operations idempotent (safe to re-run)
- Simpler than checking existence first

Rejected alternatives:
- SELECT then INSERT (more queries, race conditions)
- INSERT with try/except (ugly, exception-driven logic)

Revisit if: Need to preserve historical versions of same data

---

# Decision 009

## Use json.dumps for flexible schema columns

Date: 2026-07-20

Decision:
Store agent_outputs and critic_feedback as JSON strings.

Reason:
- SQLite has no native dict/list types
- JSON is human-readable and portable
- Avoids schema changes when agent outputs evolve

Rejected alternatives:
- Separate table per agent (too many tables, complex joins)
- Pickle (Python-only, not human-readable)
- Multiple columns per metric (rigid, breaks on changes)

Revisit if: Need to query inside JSON (then use PostgreSQL JSONB)

---

# Decision 010

## Separate fetcher from database (Adapter Pattern)

Date: 2026-07-20

Decision:
data/fetcher.py only fetches. data/db.py only stores.

Reason:
- If yfinance breaks, change one file
- If we switch to PostgreSQL, change one file
- Each module has one reason to change (Single Responsibility Principle)

Rejected alternatives:
- Combined fetch+save function (tight coupling)
- Direct yfinance calls in main.py (no abstraction)

Revisit if: Need transaction-level fetch+save atomicity

---

# Decision 011

## Make confidence auditable based on external feedback

Date: 2026-07-21

Decision:
Replace flat confidence score with component breakdown and source tracking.

Reason:
- External feedback from DDScore (Issue #13) highlighted that unverifiable confidence is dangerous
- Financial reports must be traceable to their source data and calculations
- Component breakdown makes confidence debuggable and improvable

Implementation:
- 4 components: data sufficiency (30%), metric completeness (30%), data freshness (20%), calculation stability (20%)
- Each metric carries source metadata: source API, ticker, period, calculation, timestamp
- --show-sources flag toggles between clean and audit views

Rejected alternatives:
- Keep flat confidence (ignores expert feedback, not professional)
- Implement full MemoClaimReceipt (20-column table, beyond MVP scope)
- Hide sources entirely (defeats the purpose)

Revisit if: Need full cryptographic provenance or cross-run claim verification

---

# Decision 012

## Use append-only critic history

Date: 2026-07-21

Decision:
Critic findings are never deleted, only resolved or superseded.

Reason:
- Prevents silent loss of negative feedback
- Maintains audit trail of research quality over iterations
- Aligns with DDScore feedback on immutability

Implementation:
- critic_history table with status: open, resolved, superseded
- New iterations create new records, don't update old ones
- Resolution requires explicit note and iteration reference

Rejected alternatives:
- Overwrite critic feedback each iteration (loses history)
- Delete resolved findings (not auditable)

Revisit if: Need to purge old findings for performance

---

# Decision 013

## Use requests library instead of PyGithub for GitHub API

Date: 2026-07-21

Decision:
Use raw `requests` calls to GitHub REST API instead of PyGithub library.

Reason:
- PyGithub adds abstraction that hides the API structure
- Using requests directly teaches how REST APIs work
- Easier to debug (see raw JSON, understand status codes)
- Fewer dependencies (requests is already in requirements.txt)

Rejected alternatives:
- PyGithub (hides learning opportunity, extra dependency)
- GraphQL API (more complex, overkill for MVP)

Revisit if: Need complex pagination, authentication, or enterprise features

---

# Decision 014

## Use unauthenticated GitHub API for MVP

Date: 2026-07-21

Decision:
No GitHub token required for basic functionality.

Reason:
- 60 requests/hour is enough for demo and testing
- Zero setup for users (no token to configure)
- Can add token later for higher limits

Rejected alternatives:
- Require token upfront (friction for new users)
- Use authenticated calls always (unnecessary for MVP)

Revisit if: Users hit rate limits regularly

# Decision 017 [DEPRECATED — see Decision 027]

## Hypothesis: 5% minimum floor

Date: 2026-07-26
Superseded: 2026-07-31 by Decision 027

Decision:
Add a 5% minimum probability floor so no hypothesis is ever completely dismissed.

Reason (original):
Intellectually honest — the market can always surprise you.

Why deprecated:
The floor was mathematically dishonest. It redistributed probability mass from stronger cases to weaker ones artificially. A 1% bear case forced to 5% would steal 4% from bull/base without new evidence. True intellectual honesty requires explicit uncertainty, not mathematical fudging.

Replacement:
Decision 027 — Explicit uncertainty score separate from directional bias. No artificial floors.

Rejected alternatives:
- Allow 0% probabilities (epistemically arrogant)
- Higher floor like 10% (too distorting)

Revisit if: Uncertainty modeling becomes sophisticated enough to replace floors

---

# Decision 018

## Critic Agent uses rule-based evaluation with optional LLM enhancement

Date: 2026-07-26

Decision:
Use deterministic rule checks as primary evaluation, with Ollama LLM for qualitative suggestions only when gaps are found.

Reason:
- Deterministic output: same inputs = same critique (reproducible)
- Fast execution: rule-based &lt; 10ms vs LLM 30-60s
- Transparent: every gap has a clear rule that triggered it
- LLM adds value only when needed: suggestions for complex gaps
- No dependency on Ollama availability for core functionality

Rejected alternatives:
- Pure LLM critique (slow, non-deterministic, opaque reasoning)
- No LLM at all (misses qualitative insights for gap remediation)

Revisit if: Need semantic claim verification or natural language contradiction detection

---

# Decision 019

## Risk Agent output feeds into Hypothesis Engine bear case

Date: 2026-07-26

Decision:
Individual risks and warnings from Risk Agent become evidence for the bear hypothesis.

Reason:
- DDScore #13: "Bull and bear sections must cite the same evidence register"
- Risk Agent findings are real evidence, not just minimum floor padding
- Prevents artificial 5% bear case with no supporting claims
- Makes hypothesis probabilities reflect actual risk analysis

Implementation:
- HIGH overall risk: +15% to bear
- Each individual risk: +5% to bear
- Each warning: +3% to bear
- Re-normalized after all evidence collected

Rejected alternatives:
- Keep bear case at minimum floor only (violates DDScore evidence register principle)
- Let Risk Agent directly set probabilities (breaks separation of concerns)

Revisit if: Need weighted risk severity scoring

---

# Decision 020

## Use adaptive re-runs instead of re-running every agent

Date: 2026-07-30

Decision:

Only re-run agents whose inputs can meaningfully change between iterations.

Currently:

- Quant Agent is re-run because analysis parameters can change.
- Business Agent is single-shot unless its search parameters change.
- Technical Agent is single-shot unless the repository or search scope changes.

Reason:

Running every agent on every iteration wastes computation.

Business Agent processes the same RSS articles and Technical Agent reads the same GitHub repository state, so repeated execution provides little value.

Adaptive execution:

- reduces Ollama token usage
- reduces API calls
- shortens iteration time
- prepares the system for future adaptive planning

Rejected alternatives:

- Re-run every agent every iteration (wastes compute)
- Never re-run any agent (prevents iterative improvement)

Revisit if: Business or Technical Agent inputs become adaptive between iterations.

---

# Decision 021

## Represent intentionally omitted agents as "skipped"

Date: 2026-07-30

Decision:

Agents that are intentionally omitted because required CLI arguments are missing return a status of `"skipped"` instead of an error.

The Critic Agent treats skipped agents as neutral rather than missing data.

Reason:

There is an important difference between:

- an agent that was intentionally not executed
- an agent that attempted execution and failed

Representing both cases as failures caused the Critic Agent to repeatedly report false research gaps.

Rejected alternatives:

- Return an error (breaks partial workflows)
- Return empty results (ambiguous meaning)
- Ignore missing agents entirely (loses execution state)

Revisit if: Additional execution states (e.g. deferred, cached) are introduced.

---

# Decision 022

## Do not deepen LLM reasoning on unchanged inputs

Date: 2026-07-30

Decision:

Do not repeatedly ask the LLM to generate new conclusions from identical source data.

The LLM may analyze existing extracted signals but should not attempt to discover new facts when the underlying inputs have not changed.

Reason:

Repeated prompting over identical RSS articles increases hallucination risk while providing little additional insight.

Meaningful improvement should come from:

- better input data
- improved prompts
- richer evidence

not repeated reasoning over static information.

Rejected alternatives:

- Re-run Ollama each iteration on identical RSS data (high cost, limited value)
- Allow unrestricted iterative reasoning (higher hallucination risk)

Revisit if: Business Agent gains access to new evidence or adaptive retrieval.

---

# Decision 023

## Limit Critic-driven iteration to three passes

Date: 2026-07-30

Decision:

Stop the research loop after a maximum of three iterations, even if high-risk findings remain unresolved.

Reason:

Current iterations cannot always resolve Critic feedback because several agents operate on static inputs.

The maximum iteration limit:

- prevents infinite loops
- bounds execution time
- limits API usage
- limits LLM cost

Until adaptive inputs are implemented, reaching iteration three may indicate that the system exhausted available evidence rather than fully resolving the identified risks.

Rejected alternatives:

- Continue until all gaps are resolved (can loop indefinitely)
- Stop after one iteration (loses opportunity for refinement)

Revisit if: Adaptive plan refinement allows agents to collect genuinely new evidence between iterations.


---

# Decision 027

## Kill fake probability percentages — use directional bias + uncertainty

Date: 2026-07-31

Decision:
Replace the three-way probability split (Bull% + Bear% + Base% = 100%) with two separate outputs:
1. Directional Bias: Bullish strength vs Bearish strength (raw evidence weights)
2. Uncertainty: Separate score (Scarcity + Conflict + Coverage)

Reason:
The old system produced fake probabilities. "Bear 49%" was not a probability — it was a normalized heuristic score. The 5% floor (Decision 017) actively redistributed probability mass without evidence. This violated the core principle of evidence-based research.

The new model:
- Shows raw evidence strength for each direction
- Makes uncertainty explicit and auditable
- Prevents the "base case as garbage can" problem
- Is honest about what we know and don't know

Implementation:
- `_assess_evidence()` converts register data into `EvidenceClaim` objects with direction and strength
- `_compute_directional_bias()` sums bullish vs bearish strength
- `_compute_uncertainty()` scores scarcity, conflict, coverage separately
- Base case = neutral signals, not leftover probability

Rejected alternatives:
- Keep probabilities with higher floor (still dishonest)
- Use Bayesian inference (overkill for MVP, requires priors we don't have)
- Show only directional bias without uncertainty (hides epistemic humility)

Revisit if: We develop enough data to train genuine probability models

---

# Decision 028

## Critic is an analyst, not an auditor

Date: 2026-07-31

Decision:
Redesign the Critic from a checklist auditor ("Do you have all 17 features?") to a research director ("Can you defend your thesis?").

Reason:
The old Critic produced the same output for every stock: missing 7 features after iteration 1, missing 4 after iteration 2, complete at iteration 3. It was a treadmill, not an adaptive loop.

The new Critic:
- Iteration 1 asks: "Can I form a coherent directional view?"
- Iteration 2 asks: "Did deeper data change the story?"
- Iteration 3 is a circuit breaker
- Halt when dimensions agree, not when a checklist is full

This makes the loop genuinely adaptive. AAPL halted at iteration 1 because quant and business agreed on bearish direction.

Implementation:
- 6-phase pipeline: Inventory → Signals → Dashboard → Contradictions → Active Questions → Halt
- Dashboard has 4 dimensions: Data Quality, Coverage, Agreement, Stability
- Active Questions replace `missing_evidence` feature lists

Rejected alternatives:
- Pure LLM Critic (non-deterministic, opaque, slow)
- Keep checklist but make it shorter (still a treadmill)
- Dynamic feature discovery (too complex for MVP)

Revisit if: Need semantic claim verification beyond hardcoded rules

---

# Decision 029

## Uncertainty is a separate dimension from directional conviction

Date: 2026-07-31

Decision:
Uncertainty is not "whatever probability is left over after bull and bear." It is an independently computed score.

Reason:
In the old model, Base case absorbed leftover probability mass. This meant Base was doing double duty: (a) representing neutral evidence, and (b) hiding how confused we were. A 43% base case could mean "fairly valued" or "we have no idea" — the number couldn't distinguish.

The new model separates:
- Directional Bias: "If forced to pick, which way?" (bullish/bearish/neutral)
- Uncertainty: "How much should you trust that pick?" (0-100% with factors)

This is how real analysts communicate. They say "I'm bearish, but with moderate uncertainty because I only have 2 of 3 dimensions."

Implementation:
- Uncertainty = Scarcity (few signals) + Conflict (dimensions disagree) + Coverage (missing dimensions)
- Each factor is independently computed and exposed in output
- Uncertainty score has levels: Low, Moderate, Elevated, High, Extreme

Rejected alternatives:
- Keep base case as uncertainty proxy (ambiguous)
- Use variance of agent outputs (requires multiple runs)
- Ask LLM "how confident are you?" (not auditable)

Revisit if: We develop predictive confidence calibration

---

# Decision 030

## Dashboard-driven halt logic

Date: 2026-07-31

Decision:
The loop halts based on the Critic's Dashboard, not on a feature checklist.

Reason:
Old halt condition: `missing_evidence` empty OR `MAX_ITERATIONS` reached. This meant every healthy stock ran all 3 iterations because the checklist had 17 items.

New halt conditions (iteration-aware):
- Iteration 1: Halt if Coverage &gt;= 50%, Agreement = High, no critical contradictions
- Iteration 2: Halt if Stability = Stable (hypotheses didn't shift with deeper data)
- Iteration 3: Always halt (circuit breaker)

This means most assets halt early. Only messy, contradictory assets run all 3 iterations. The number of iterations becomes information about the asset.

Implementation:
- Dashboard computes 4 scores: Data Quality, Coverage, Agreement, Stability
- Halt decision reads Dashboard and iteration number
- Active Questions track what would need to be answered to continue

Rejected alternatives:
- Halt when all features present (treadmill)
- Halt when confidence &gt; threshold (confidence was fake anyway)
- Let LLM decide when to stop (non-deterministic, dangerous)

Revisit if: Need more sophisticated stopping rules (e.g., cost-benefit of deeper data)

---

# Decision 031

## Evidence Register as single source of truth

Date: 2026-07-31

Decision:
All agents read from and write to a central Evidence Register. No agent passes outputs directly to another agent.

Reason:
The old system had agents returning dicts that were passed downstream. This created tight coupling: if Quant's output format changed, Risk and Hypotheses broke.

The Evidence Register decouples agents:
- Each agent writes its findings to the register with provenance
- Downstream agents read what they need from the register
- The register tracks: source agent, tier, data_points, data_period, timestamp
- Trustworthiness checks ensure statistical validity

This is the core architectural change that enabled Issue #9b+.

Implementation:
- `core/evidence.py`: `EvidenceRegister` class with `add()`, `get()`, `has()`, `is_trustworthy()`, `snapshot()`
- `EvidenceItem` dataclass: value, source, timestamp, tier, data_points, data_period
- Loop controller passes register to all agents

Rejected alternatives:
- Message passing between agents (complex, fragile)
- Direct function calls (tight coupling)
- Database as register (too slow for iteration)

Revisit if: Need persistence across sessions or distributed agents

---

# Decision 032

## Use Jinja2 templating for report generation instead of inline string formatting

Date: 2026-08-05

Decision:
Use Jinja2 with a dedicated `.md.j2` template file for the Report Generator instead of building the report through Python f-strings or concatenation.

Reason:
- Separation of concerns: report structure lives in a template, data formatting lives in Python
- Templates are human-readable and editable without touching generator logic
- Supports conditional sections (skip empty tables, show/hide tiers) cleanly
- Reusable across different report types without code changes
- Designers or non-developers can modify output format without understanding Python

Rejected alternatives:
- Inline f-strings (tight coupling, hard to maintain, ugly with conditional logic)
- Python `string.Template` (too limited for tables and conditionals)
- Pure LLM-generated reports (non-deterministic, no structure guarantees, expensive)

Revisit if: Need dynamic template selection per asset type or multi-format output (HTML, DOCX)

---

# Decision 033

## Implement Audit Trail with graded scoring

Date: 2026-08-13

Decision:
Store every research session in `research_sessions` and compare against actual 30-day market outcomes using a graded score (-1.0 to +1.0), not binary correct/incorrect.

Reason:
- Binary correct/incorrect loses signal. A bearish bias with -3% move is partially correct, not a "loss."
- Graded scoring rewards directional magnitude: +5% on bullish = perfect, +10% still = perfect (capped), -5% = completely wrong.
- Neutral is not a free pass: big moves against neutral incur penalty.

Implementation:
- `score_outcome(bias, price_change_30d)` in `data/audit.py`
- Bullish: `min(1.0, price_change / 5.0)`
- Bearish: `min(1.0, -price_change / 5.0)`
- Neutral: `1.0` if |move| ≤ 2%, else `1.0 - (|move| - 2.0) / 5.0`

Rejected alternatives:
- Binary correct/incorrect (too coarse)
- Raw price change as score (unbounded, hard to compare across assets)
- Sharpe/Sortino ratios (deferred to Phase 12)

---

# Decision 034

## Use inline JSON snapshots, not separate files

Date: 2026-08-13

Decision:
Store the full Evidence Register snapshot as inline TEXT (JSON string) in the `research_sessions` row, not as external files or a separate table.

Reason:
- Single-row retrieval: get session + snapshot in one query
- No file path management or cleanup needed
- SQLite TEXT handles multi-MB JSON fine for MVP scale
- `NumpyEncoder` handles `np.float64`, `np.int64` serialization safely

Rejected alternatives:
- Separate `evidence_snapshots` table (more joins, more complexity)
- External JSON files (path management, git noise, cleanup risk)
- Pickle blobs (Python-only, not human-readable)

Revisit if: Snapshots exceed 10MB or need partial querying inside JSON

---

# Decision 035

## Fresh start for audit trail — no migration from loop_states

Date: 2026-08-13

Decision:
`research_sessions` starts empty. Old `loop_states` remains untouched. No backfill of historical loop executions.

Reason:
- `loop_states` schema lacks the fields needed for audit (sector, bull/bear strength, evidence snapshot)
- Backfill would require reconstructing evidence registers from partial data — unreliable
- Clean separation: `loop_states` = execution audit log, `research_sessions` = research quality audit

Rejected alternatives:
- Migrate old loop_states (complex, incomplete data)
- Dual-write to both tables (unnecessary coupling)

---

# Decision 036

## Strict sector validation — unknown sectors are errors

Date: 2026-08-13

Decision:
`--sector` CLI flag and watchlist JSON both enforce strict canonical sector validation. Unknown sectors exit with code 1, not silently become NULL.

Reason:
- Silent NULLs create dirty data that pollutes audit grouping
- Strict validation forces consistency at entry time
- Fuzzy matching + aliases handle common typos (`ai` → `generative-ai`)
- Watchlist loader validates ALL sectors at startup (fail fast)

Rejected alternatives:
- Silent NULL on unknown sector (creates unclean audit data)
- Auto-detection via LLM (expensive, non-deterministic, overkill for MVP)