# ARCHITECTURE.md

# Autonomous Investment Research System (AIRS)

## Purpose

This document explains the technical architecture of the **Autonomous Investment Research System (AIRS)**.

The goal is to build a modular AI research platform that collects information, analyzes evidence, evaluates research quality, and generates professional investment research reports.

---

# System Overview

The system consists of six major architectural layers.

```text
                     User
                      │
                      │
             Research Request
                      │
                      ▼

        Research Controller Layer
             (Loop Engine)
                      │
      ─────────────────────────────────
      │               │               │
      ▼               ▼               ▼
 External        Analysis        LLM Reasoning
  Sources         Modules         Components
                      │
                      ▼
             Evidence Register
                      │
                      ▼
               Critic Agent
                      │
                      ▼
            Hypothesis Engine
                      │
                      ▼
            Report Generator
                      │
                      ▼
             Investment Memo
```

---

# Layer 1 — Data Layer

Responsible for collecting and preparing information for analysis.

## Data Sources

- Yahoo Finance (`yfinance`)
- GitHub API
- RSS Feeds
- Public Documents

## Responsibilities

- Data collection
- Data cleaning
- Data normalization
- Data storage

---

# Layer 2 — Database Layer

## Database

- SQLite

## Stores

- Entities
- Historical market data
- Technical activity
- News
- Research states
- Reports
- Loop iteration history (including dashboard snapshots)

---

# Layer 3 — Agent Layer

Agents are specialized analysis modules.

All agents read from and write to the **Evidence Register**.

---

## Quant Agent

### Purpose

Handles numerical market analysis using tiered computation.

### Input

- Market data

### Output

- Trend analysis
- Volatility
- Momentum
- Risk metrics
- RSI
- MACD
- ATR
- Volume profile
- Beta
- Correlation matrix

### Technology

- Python
- pandas
- numpy

No LLM required.

### Tiered Computation

#### Tier 1 (3 Months)

- Returns
- Volatility
- Momentum
- Moving averages
- Drawdown
- Risk score
- Trend

#### Tier 2 (6 Months)

Everything from Tier 1 plus:

- RSI
- MACD
- Volume profile

#### Tier 3 (1 Year)

Everything from Tier 2 plus:

- ATR
- Volatility regime
- Beta
- Correlation matrix

---

## Technical Agent

### Purpose

Analyzes engineering ecosystem health.

### Input

- GitHub data

### Output

- Developer activity
- Project health
- Maintenance signals

### Technology

- Python
- GitHub API

Uses an LLM only for summary generation.

Runs **once per session** during bootstrap.

---

## Business Agent

### Purpose

Analyzes business activity.

### Input

- News
- Public information

### Output

- Business catalysts
- Business signals (positive, negative, neutral)
- Risks

### Technology

- Python
- Ollama (summarization only)

Runs **once per session** during bootstrap.

---

## Risk Agent

### Purpose

Identifies weaknesses and potential risks.

### Output

- Risk factors with categories and severity
- Cross-agent contradictions
- Blind-spot warnings

### Technology

- Rule-based analysis

Reads from the Evidence Register via the legacy bridge.

---

## Critic Agent

### Purpose

Evaluates overall research quality and directs the research process.

### Architecture (6-Phase Pipeline)

1. **Inventory**
   - Catalog available evidence
   - Detect missing features

2. **Directional Signals**
   - Extract bullish, bearish, and neutral signals

3. **Dashboard**
   - Compute auditable confidence dimensions:
     - Data Quality
     - Coverage
     - Agreement
     - Stability (iteration-over-iteration comparison)

4. **Contradictions**
   - Execute 12 hardcoded cross-agent contradiction rules

5. **Active Questions**
   - Generate specific research questions
   - Focus on investigation rather than feature checklists

6. **Halt Decision**
   - **Iteration 1:** Can a coherent directional view be formed?
   - **Iteration 2:** Did deeper data change the thesis?
   - **Iteration 3:** Circuit breaker

### Technology

- 100% rule-based decision making
- Optional Ollama suggestions (display only, never binding)

---

# Layer 4 — Evidence Register

**Location**

```text
core/evidence.py
```

The Evidence Register is the central in-memory accumulator with provenance tracking.

## Responsibilities

- Single source of truth for all agent outputs
- Provenance tracking
  - Source agent
  - Tier
  - Data points
  - Data period
  - Timestamp
- Trustworthiness validation
- Snapshot support
- Query support

## Design

- Plain Python dictionary
- `EvidenceItem` dataclasses
- No database
- No microservices
- Existing entries are overwritten when deeper analysis becomes available

---

# Layer 5 — Hypothesis Engine

**Location**

```text
reports/hypothesis.py
```

Generates investment hypotheses from the Evidence Register.

## Output Structure

### Directional Bias

Bullish strength versus bearish strength based on raw evidence weights.

> Not normalized probabilities.

### Uncertainty

Independent uncertainty score based on:

- Scarcity
- Conflict
- Coverage

### Claims

Each claim includes:

- Source
- Raw value
- Strength
- Description
- Direction

### Base Case

Represents neutral or moderate signals.

Not a "leftover probability."

## Design Principles

- No artificial probability floors
- No normalization to 100%
- Every claim is traceable to its evidence source
- Uncertainty is explicit instead of hidden inside probabilities

---

# Layer 6 — Loop Controller

**Location**

```text
controller/loop.py
```

Controls workflow execution using convergent evidence accumulation.

## Workflow

```text
Capability Probe
      │
      ▼
Bootstrap
(Business + Technical)
      │
      ▼
Iterative Evidence Accumulation
      │
      ▼
Iteration 1
Quant Tier 1
      │
      ▼
Critic
(Coherent View?)
      │
      ▼
Iteration 2
Quant Tier 2
      │
      ▼
Critic
(Stable Thesis?)
      │
      ▼
Iteration 3
Quant Tier 3
      │
      ▼
Critic
(Circuit Breaker)
      │
      ▼
Final Output Generation
      │
      ▼
Risk + Hypotheses
```

## Key Behaviors

- Business and Technical agents run once per session
- Quant Agent is the only iterative agent

The loop halts when:

- All dimensions agree on direction
- Hypotheses stabilize across iterations
- Active questions cannot be answered with deeper data
- `MAX_ITERATIONS = 3`

---

# Layer 7 — LLM Layer

## Responsibilities

- Planning
- Reasoning
- Qualitative critique
- Report writing
- News summarization
- Signal extraction

## LLMs Are **Not** Used For

- Calculations
- Simple data processing
- Database operations
- Feature selection
- Halt decisions
- Confidence score computation

## Runtime

- Ollama

## Supported Models

- Qwen 2.5 7B
- Llama 3.1 8B
- Mistral 7B

---

# Error Handling Strategy

| Failure | Handling Strategy |
|----------|-------------------|
| API timeout | Retry up to 3 times with exponential backoff, then use cached data if available |
| Empty data | Log a warning, skip the affected agent, and continue with partial analysis |
| LLM unavailable | Fall back to rule-based analysis. Critic and Hypothesis Engine continue functioning |
| Database locked | Wait 1 second, retry, then fail gracefully if unsuccessful |
| GitHub rate limit | Use unauthenticated fallback when possible and flag data limitations |

---

# Design Principles

- Modular architecture
- Local-first development
- Minimize API costs (target: **$0**)
- Produce human-readable outputs
- Base conclusions on evidence
- Prefer controlled iteration over uncontrolled autonomy
- The Critic acts as an analyst, not an auditor
- Uncertainty is treated as a first-class output