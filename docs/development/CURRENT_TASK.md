# CURRENT_TASK.md

# Current Development Status

**Last Updated:** 2026-08-05

---

# Current Phase

| Phase | Status |
|-------|--------|
| Phase 1 — Data Foundation | ✅ Complete |
| Phase 2 — Quant Agent | ✅ Complete |
| Phase 3 — Technical Agent | ✅ Complete |
| Phase 4 — Business Agent | ✅ Complete |
| Phase 5 — Risk Agent | ✅ Complete |
| Phase 6 — Critic Agent | ✅ Complete |
| Phase 7 — Loop Controller | ✅ Complete |
| Phase 8 — Report Generator (Issue #10) | ✅ Complete |
| Phase 9 — Audit Trail & Backtesting | 📅 Planned |

---

# Completed Milestones

- [x] **2026-07-19** — Defined project idea → Issue #1
- [x] **2026-07-19** — Created documentation system → Issue #2
- [x] **2026-07-20** — Project scaffold and folder structure → Issue #1
- [x] **2026-07-20** — Database schema (SQLite, 4 tables) → Issue #2
- [x] **2026-07-20** — Market data fetcher (Yahoo Finance with retry logic) → Issue #3
- [x] **2026-07-20** — Quant Agent v1 (returns, volatility, momentum, drawdown, risk score, trend) → Issue #4
- [x] **2026-07-21** — Quant Agent v2 (auditable confidence using DDScore feedback)
- [x] **2026-07-21** — Technical Agent (GitHub API integration, repository health scoring) → Issue #5
- [x] **2026-07-23** — Business Agent (news analysis using Ollama LLM) → Issue #6
- [x] **2026-07-23** — Risk Agent (downside analysis and contradiction detection) → Issue #7
- [x] **2026-07-26** — Critic Agent (research quality evaluation and cross-agent validation) → Issue #8
- [x] **2026-07-26** — Hypothesis Competition Engine v2 (Risk Agent feeds bear case, Critic triggers iteration)
- [x] **2026-07-30** — Loop Controller (iterative orchestration, persistence, Critic-driven execution) → Issue #9
- [x] **2026-08-05** — Report Generator (Jinja2 Markdown + optional PDF investment memo) → Issue #10

---

# Active Issue

| Item | Value |
|------|-------|
| **Issue** | #10 — Report Generator |
| **Status** | ✅ Complete |
| **Branch** | `feature/#10-report-generator` |

---

# Next Tasks (Priority Order)

1. **Update `README.md`**
   - Reflect v0.3.7 features
   - Document report generation
   - Update CLI examples

2. **Phase 9 — Audit Trail & Backtesting**
   - Store session snapshots
   - Track recommendation accuracy over time
   - Enable historical evaluation

3. **Issue #11 — Ollama Integration Improvements**
   - Priority: **Medium**

---

# Current CLI Commands

## Quant Analysis

```bash
python main.py --entity AAPL --quant-only
```

## Technical Analysis

```bash
python main.py --repo bitcoin/bitcoin --technical-only
```

## Business Analysis

```bash
python main.py --entity NVIDIA --business-only
```

## Risk Analysis

```bash
python main.py --entity AAPL --repo apple/swift --hypotheses
```

## Full Research Pipeline

```bash
python main.py --entity AAPL \
    --repo apple/swift \
    --ticker AAPL \
    --hypotheses
```

## Full Pipeline (Without Repository)

```bash
python main.py \
    --entity AAPL \
    --ticker AAPL \
    --hypotheses
```

## Source Tracking

```bash
python main.py \
    --entity AAPL \
    --quant-only \
    --show-sources
```

## Generate Investment Memo

### Markdown

```bash
python main.py \
    --entity AAPL \
    --ticker AAPL \
    --repo apple/swift \
    --hypotheses
```

### Markdown + PDF

```bash
python main.py \
    --entity AAPL \
    --ticker AAPL \
    --repo apple/swift \
    --hypotheses \
    --pdf
```

---

# Current Status

## Blockers

**None**

---

# System Notes

### Technical Agent

- Uses the GitHub REST API directly via the `requests` library.
- GitHub unauthenticated rate limit: **60 requests/hour**.

### Business Agent

- Uses **Ollama (`qwen2.5:7b`)** for:
  - News summarization
  - Signal extraction
  - Business insights

### Risk Agent

- Fully rule-based (no LLM).
- Provides deterministic downside and contradiction detection.

### Critic Agent

- Reviews outputs from all agents.
- Identifies research gaps.
- Suggests improvements.
- Decides whether another research iteration is required.

### Loop Controller

- Orchestrates:

```
Plan
    ↓
Research
    ↓
Analyze
    ↓
Critique
    ↓
Iterate (maximum 3 rounds)
```

Additional behavior:

- Supports graceful skipping of unavailable agents.
- Persists execution state in the `loop_states` database table.
- Controlled by the Critic Agent's `should_iterate` decision.

### Report Generator

- Produces professional Markdown investment memos.
- Optional PDF export via WeasyPrint.
- Seven-section investment report.

### Hypothesis Engine

- Uses directional bias.
- Explicitly models uncertainty.
- Avoids fabricated probabilities.
- Risk Agent evidence contributes directly to the bear case.

---

# Known Limitations

- **Business Agent**
  - RSS feeds are live-only, so results change little across iterations.

- **Technical Agent**
  - Reuses the same GitHub repository snapshot unless repository data changes.

- **Loop Refinement**
  - `_refine_plan()` currently records refinement intent but does not yet modify subsequent agent inputs.

- **Iteration Updates**
  - Only the Quant Agent currently receives updated inputs between iterations.

- **PDF Export**
  - Windows requires GTK+ system libraries for the WeasyPrint dependency.

---

# Overall Progress

**Current Version:** `v0.3.7`

```
████████████████████████████████████████░░░░ 89%

Completed
├── Data Foundation
├── Quant Agent
├── Technical Agent
├── Business Agent
├── Risk Agent
├── Critic Agent
├── Loop Controller
└── Report Generator

Remaining
└── Audit Trail & Backtesting
```