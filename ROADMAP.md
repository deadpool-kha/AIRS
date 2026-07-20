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
- [ ] GitHub repository initialized
- [ ] Python virtual environment created
- [ ] Folder structure created
- [ ] README.md with project overview
- [ ] requirements.txt with pinned dependencies
- [ ] .gitignore configured
- [ ] All documentation files (.md) in place
- [ ] First commit pushed

### Estimated: 1-2 days
### Blocked by: Nothing
### Blocks: Phase 1

---

# Phase 1: Data Foundation

## Goal: System can collect and store market data

### Definition of Done:
- [ ] SQLite schema created and tested
- [ ] market_data table with proper indexes
- [ ] entities table
- [ ] research_states table (for loop tracking)
- [ ] yfinance fetcher working (AAPL, BTC-USD)
- [ ] Data persists across script runs
- [ ] Error handling for API failures
- [ ] Unit tests for fetcher and db modules

### Estimated: 3-5 days
### Blocked by: Phase 0
### Blocks: Phase 2

---

# Phase 2: Quant Agent

## Goal: System produces quantitative analysis

### Definition of Done:
- [ ] Calculate returns (daily, weekly, monthly)
- [ ] Calculate volatility (standard deviation)
- [ ] Calculate momentum (rate of change)
- [ ] Calculate drawdown (max peak-to-trough)
- [ ] Calculate risk score
- [ ] Output structured dict with confidence
- [ ] No LLM used — pure Python/pandas
- [ ] Unit tests

### Estimated: 2-3 days
### Blocked by: Phase 1
### Blocks: Phase 5 (Loop needs all agents)

---

# Phase 3: Technical Agent

## Goal: System evaluates technical ecosystem health

### Definition of Done:
- [ ] GitHub API integration (unauthenticated)
- [ ] Fetch commits, contributors, issues, releases
- [ ] Calculate contributor growth rate
- [ ] Calculate commit frequency
- [ ] Assess project maintenance health
- [ ] Output structured dict
- [ ] Handle rate limits gracefully

### Estimated: 3-4 days
### Blocked by: Phase 1
### Blocks: Phase 5

---

# Phase 4: Business Agent

## Goal: System understands qualitative information

### Definition of Done:
- [ ] RSS/news fetching capability
- [ ] Local LLM (Ollama) summarization
- [ ] Extract catalysts and events
- [ ] Output structured dict with sources
- [ ] Fallback when no news found

### Estimated: 2-3 days
### Blocked by: Phase 1
### Blocks: Phase 5

---

# Phase 5: Loop Engine

## Goal: System can iterate and improve research quality

### Definition of Done:
- [ ] Loop controller implemented
- [ ] Critic Agent evaluates all outputs
- [ ] Identifies gaps in research
- [ ] Generates targeted iteration plan
- [ ] Max 3 iterations enforced
- [ ] Falls back to best-effort report
- [ ] Loop state persisted to database

### Estimated: 3-4 days
### Blocked by: Phase 2, 3, 4
### Blocks: Phase 6

---

# Phase 6: Risk Agent

## Goal: System identifies downside and weaknesses

### Definition of Done:
- [ ] Analyze negative signals from all agents
- [ ] Identify competition and regulatory risks
- [ ] Assess concentration and volatility risks
- [ ] Output structured risk assessment
- [ ] Uses rules + LLM reasoning

### Estimated: 2-3 days
### Blocked by: Phase 2, 3, 4
### Blocks: Phase 7

---

# Phase 7: Report Generator

## Goal: System generates professional investment memo

### Definition of Done:
- [ ] Combine all agent outputs
- [ ] Local LLM writes structured report
- [ ] Markdown output with sections
- [ ] Includes confidence levels
- [ ] Cites evidence and sources
- [ ] Handles partial data gracefully

### Estimated: 2-3 days
### Blocked by: Phase 5, 6
### Blocks: Phase 8

---

# Phase 8: Interface and Presentation

## Goal: Project is presentable

### Definition of Done:
- [ ] Streamlit interface (optional)
- [ ] README with screenshots
- [ ] Architecture diagram
- [ ] Demo video or GIF
- [ ] Example reports in repo
- [ ] Deployed or easily runnable

### Estimated: 2-3 days
### Blocked by: Phase 7
### Blocks: Nothing

---

# Minimum Viable Version

If time becomes limited:

Must have:
- [x] Quant Agent
- [x] Technical Agent
- [x] Loop Controller
- [x] Critic Agent
- [x] LLM Report Generator

Optional:
- [ ] Streamlit UI
- [ ] Business Agent (can use placeholder)
- [ ] Advanced ML

---

# Future Improvements

Not part of MVP:

* real-time monitoring
* portfolio management
* trading execution
* more agents
* cloud deployment
* user accounts
* mobile app
* on-chain data integration (Phase 2 extension)

---

# Success Criteria

The project is successful if:

1. A stranger can understand it from GitHub.
2. A user can run an analysis.
3. The system produces a structured report.
4. The loop demonstrates self-improving research.
5. Architecture demonstrates modern AI engineering.
6. The developer can explain every design decision.