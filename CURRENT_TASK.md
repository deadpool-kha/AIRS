# CURRENT_TASK.md

# Current Development Status

**Last Updated:** 2026-07-26

---

# Current Phase

- ✅ Phase 1: Data Foundation (COMPLETE)
- ✅ Phase 2: Quant Agent (COMPLETE)
- ✅ Phase 3: Technical Agent (COMPLETE)
- ✅ Phase 4: Business Agent (COMPLETE)
- ✅ Phase 5: Risk Agent (COMPLETE)
- ✅ Phase 6: Critic Agent (COMPLETE)

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

---

# Active Issue

- **Issue #9:** Implement Loop Controller
  - **Status:** Not Started
  - **Branch:** `feature/#9-loop-controller` (when ready)

---

# Next Tasks (Priority Order)

1. **#9:** Implement Loop Controller (orchestrate agent iteration) — **Priority:** High
2. **#10:** Complete Report Generator (integrate all agents, Critic findings, hypothesis engine) — **Priority:** High
3. **#11:** Ollama integration polish — **Priority:** Medium

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

# Full pipeline with hypothesis generation and Critic evaluation
python main.py --entity AAPL --repo apple/swift --ticker AAPL --hypotheses

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
- Critic triggers iteration when HIGH risk is found and iteration < 3
- Hypothesis engine applies a 5% minimum floor (DDScore #13)
- Risk Agent output feeds into bear case evidence (not just the minimum floor)
- API discovery method documented in `LEARNING.md`
