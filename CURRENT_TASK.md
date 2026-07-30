# CURRENT_TASK.md

# Current Development Status

**Last Updated:** 2026-07-30

---

# Current Phase

- ✅ Phase 1: Data Foundation (COMPLETE)
- ✅ Phase 2: Quant Agent (COMPLETE)
- ✅ Phase 3: Technical Agent (COMPLETE)
- ✅ Phase 4: Business Agent (COMPLETE)
- ✅ Phase 5: Risk Agent (COMPLETE)
- ✅ Phase 6: Critic Agent (COMPLETE)
- ✅ Phase 7: Loop Controller (COMPLETE)

---

# Completed

- [x] 2026-07-19: Defined project idea → Issue #1
- [x] 2026-07-19: Created documentation system → Issue #2
- [x] 2026-07-20: Project scaffold and folder structure → Issue #1
- [x] 2026-07-20: Database schema (SQLite, 4 tables) → Issue #2
- [x] 2026-07-20: Market data fetcher (yfinance with retry) → Issue #3
- [x] 2026-07-20: Quant Agent v1 (returns, volatility, momentum, drawdown, risk score, trend) → Issue #4
- [x] 2026-07-21: Quant Agent v2 — auditable confidence based on DDScore feedback
- [x] 2026-07-21: Technical Agent (GitHub API: commits, contributors, repo info, health score) → Issue #5
- [x] 2026-07-23: Business Agent (news analysis with Ollama LLM) → Issue #6
- [x] 2026-07-23: Risk Agent (downside analysis, cross-agent contradiction detection) → Issue #7
- [x] 2026-07-26: Critic Agent (research quality evaluation, cross-agent validation, LLM-enhanced suggestions) → Issue #8
- [x] 2026-07-26: Hypothesis Competition Engine v2 — Risk Agent feeds into bear case, Critic triggers iteration on HIGH risk
- [x] 2026-07-30: Loop Controller (iterative orchestration, graceful agent skipping, database persistence, Critic-driven iteration) → Issue #9

---

# Active Issue

- **Issue #10:** Report Generator
  - **Status:** Not Started
  - **Branch:** `feature/#10-report-generator`

---

# Next Tasks (Priority Order)

1. **#10:** Report Generator (integrate all agents into a structured Markdown/PDF investment memo) — **Priority:** High
2. **#11:** Ollama integration polish — **Priority:** Medium

---

# What Works Right Now

```bash
# Quant analysis only
python main.py --entity AAPL --quant-only

# Technical analysis only
python main.py --repo bitcoin/bitcoin --technical-only

# Business analysis only
python main.py --entity NVIDIA --business-only

# Risk analysis (requires other agents, use --hypotheses)
python main.py --entity AAPL --repo apple/swift --hypotheses

# Full iterative research pipeline (up to 3 Critic-guided iterations)
python main.py --entity AAPL --repo apple/swift --ticker AAPL --hypotheses

# Works without a repository (Technical Agent skipped)
python main.py --entity AAPL --ticker AAPL --hypotheses

# With source tracking
python main.py --entity AAPL --quant-only --show-sources
```

---

# Current Blockers

- None

---

# Notes

- Technical Agent uses GitHub REST API directly (`requests` library)
- Free tier: 60 requests/hour (unauthenticated)
- Business Agent uses Ollama (`qwen2.5:7b`) for summarization and signal extraction
- Risk Agent is rules-based (no LLM) for deterministic risk detection
- Critic Agent evaluates all agent outputs, flags gaps, and suggests improvements
- Loop Controller orchestrates Plan → Research → Analyze → Critique → Iterate (maximum of 3 iterations)
- Critic Agent controls loop continuation using the `should_iterate` decision
- Agents can be intentionally skipped (e.g., missing `--repo` or `--ticker`) without terminating execution
- Loop state is persisted in the `loop_states` database table
- Hypothesis engine applies a 5% minimum floor (DDScore #13)
- Risk Agent output feeds into bear case evidence (not just the minimum floor)
- API discovery method documented in `LEARNING.md`

## Known Limitations

- Business Agent (RSS) produces largely static results across iterations because RSS feeds are live-only.
- Technical Agent reuses the same GitHub repository snapshot across iterations unless the repository changes.
- `_refine_plan()` currently logs refinement intent but does not yet modify agent inputs (planned enhancement).
- Only the Quant Agent currently benefits from updated inputs between iterations.