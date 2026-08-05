# AIRS Architecture — Autonomous Investment Research System

## Purpose

This document explains the technical architecture of the **Autonomous Investment Research System (AIRS)**.

The goal is to build a modular AI research platform that collects information, analyzes evidence, evaluates research quality, and generates professional investment research reports.

---

# System Overview

The system consists of **eight major architectural layers** plus two supporting infrastructures.

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
               Risk Agent
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

- Yahoo Finance (yfinance)
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

SQLite

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

All agents read from and write to the Evidence Register.

---

# Quant Agent

## Purpose

Handles numerical market analysis using tiered computation.

## Input

- Market data

## Output

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

## Technology

- Python
- pandas
- numpy

No LLM required.

---

## Tiered Computation

### Tier 1 (3 Months)

- Returns
- Volatility
- Momentum
- Moving averages
- Drawdown
- Risk score
- Trend

---

### Tier 2 (6 Months)

Everything from Tier 1 plus:

- RSI
- MACD
- Volume profile

---

### Tier 3 (1 Year)

Everything from Tier 2 plus:

- ATR
- Volatility regime
- Beta
- Correlation matrix

---

# Technical Agent

## Purpose

Analyzes engineering ecosystem health.

## Input

- GitHub data

## Output

- Developer activity
- Project health
- Maintenance signals

## Technology

- Python
- GitHub API

Uses an LLM only for summary generation.

Runs once per session during bootstrap.

---

# Business Agent

## Purpose

Analyzes business activity.

## Input

- News
- Public information

## Output

- Business catalysts
- Business signals (positive, negative, neutral)
- Risks

## Technology

- Python
- Ollama (summarization only)

Runs once per session during bootstrap.

---

# Risk Agent

## Purpose

Identifies weaknesses and potential risks.

## Output

- Risk factors with categories and severity
- Cross-agent contradictions
- Blind-spot warnings

## Technology

- Rule-based analysis

Reads from the Evidence Register via the legacy bridge.

---
# Layer 4 — Evidence Register

## Location

```text
core/evidence.py
```

The Evidence Register is the central in-memory accumulator with provenance tracking.

---

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

---

## Design

- Plain Python dictionary
- EvidenceItem dataclasses
- No database
- No microservices
- Existing entries are overwritten when deeper analysis becomes available

---

# Layer 5 — Critic Agent

## Location

```text
agents/critic.py
```

Evaluates overall research quality and directs the research process.

---

# Architecture (6-Phase Pipeline)

## 1. Inventory

- Catalog available evidence
- Detect missing features

---

## 2. Directional Signals

Extract:

- Bullish signals
- Bearish signals
- Neutral signals

---

## 3. Dashboard

Compute auditable confidence dimensions:

- Data Quality
- Coverage
- Agreement
- Stability (iteration-over-iteration comparison)

---

## 4. Contradictions

Execute 12 hardcoded cross-agent contradiction rules.

---

## 5. Active Questions

Generate specific research questions.

Focus on investigation rather than feature checklists.

---

## 6. Halt Decision

The Critic evaluates whether more research is required.

### Iteration 1

Can a coherent directional view be formed?

### Iteration 2

Did deeper data change the thesis?

### Iteration 3

Circuit breaker.

---

## Technology

- 100% rule-based decision making
- Optional Ollama suggestions (display only, never binding)

---

# Layer 6 — Hypothesis Engine

## Location

```text
reports/hypothesis.py
```

Generates investment hypotheses from the Evidence Register.

---

# Output Structure

## Directional Bias

Bullish strength versus bearish strength based on raw evidence weights.

Not normalized probabilities.

---

## Uncertainty

Independent uncertainty score based on:

- Scarcity
- Conflict
- Coverage

---

## Claims

Each claim includes:

- Source
- Raw value
- Strength
- Description
- Direction

---

## Base Case

Represents neutral or moderate signals.

Not a "leftover probability."

---

# Design Principles

- No artificial probability floors
- No normalization to 100%
- Every claim is traceable to its evidence source
- Uncertainty is explicit instead of hidden inside probabilities

---

# Layer 7 — Risk Agent

## Location

```text
agents/risk.py
```

Performs deterministic downside analysis using existing agent outputs.

---

## Responsibilities

- Identify risk factors with severity classification (high / medium / low)
- Detect cross-agent contradictions
- Issue blind-spot warnings (e.g., all-positive signal bias)
- Feed risk evidence into the bear case of the Hypothesis Engine

---

## Design

- 100% rule-based
- No LLM involvement
- Reads from Evidence Register (currently via legacy bridge; direct integration planned in Phase 9)

---

# Layer 8 — Report Generator

## Location

```text
reports/generator.py
```

Produces professional investment research memos from loop results.

---

# Design

- Jinja2 templating for clean separation of logic and presentation
- Deterministic data formatting (no LLM for numbers or tables)
- Optional LLM-enhanced executive summary prose
- Graceful degradation when data is missing
- PDF generation attempts WeasyPrint; falls back gracefully if unavailable

---

# Report Sections

## Executive Summary

- Directional bias
- Uncertainty
- Halt reason

---

## Audit Dashboard

- Data Quality
- Coverage
- Agreement
- Stability

---

## Investment Thesis

Includes:

### Bull Case

Evidence table:

- Source
- Strength
- Raw Value

### Bear Case

Evidence table.

### Base / Neutral Case

Evidence table.

---

## Uncertainty Analysis

Includes:

- Scarcity
- Conflict
- Coverage

---

## Evidence Register Summary

Includes:

- Evidence by Source
- Evidence by Tier
- Quantitative Evidence (full metrics table)
- Business Evidence (signals, catalysts, risks)
- Technical Evidence (health metrics)

---

## Risk Assessment

Includes:

- Severity-classified risk tables
- Warning tables

---

## Active Questions & Unresolved Contradictions

---

## Appendix

Includes:

- Methodology
- Design Principles
- Limitations
- Disclaimer

---
# Integration

The Report Generator is invoked automatically at the end of the `--hypotheses` workflow via:

```text
controller/loop.py → _final_output()
```

---

# CLI

```bash
--pdf    # Attempts PDF export; gracefully skips if weasyprint unavailable
```

---

# Orchestration Layer — Loop Controller

## Location

```text
controller/loop.py
```

Controls workflow execution using convergent evidence accumulation.

---

# Workflow

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
Risk + Hypotheses + Report
```

---

# Key Behaviors

- Business and Technical agents run once per session
- Quant Agent is the only iterative agent
- Report Generator runs once after the loop halts

The loop halts when:

- All dimensions agree on direction
- Hypotheses stabilize across iterations
- Active questions cannot be answered with deeper data

```text
MAX_ITERATIONS = 3
```

---

# Cross-Cutting Layer — LLM Layer

## Responsibilities

LLMs are responsible for:

- Planning
- Reasoning
- Qualitative critique
- Report writing
- News summarization
- Signal extraction

---

# LLMs Are Not Used For

LLMs are not used for:

- Calculations
- Simple data processing
- Database operations
- Feature selection
- Halt decisions
- Confidence score computation

---

# Runtime

Ollama

---

# Supported Models

- Qwen 2.5 7B
- Llama 3.1 8B
- Mistral 7B

---

# Error Handling Strategy

| Failure | Handling Strategy |
|---|---|
| API timeout | Retry up to 3 times with exponential backoff, then use cached data if available |
| Empty data | Log a warning, skip the affected agent, and continue with partial analysis |
| LLM unavailable | Fall back to rule-based analysis. Critic and Hypothesis Engine continue functioning |
| Database locked | Wait 1 second, retry, then fail gracefully if unsuccessful |
| GitHub rate limit | Use unauthenticated fallback when possible and flag data limitations |
| PDF generation missing | Log warning, skip PDF, keep Markdown output |

---

# Design Principles

- Modular architecture
- Local-first development
- Minimize API costs (target: $0)
- Produce human-readable outputs
- Base conclusions on evidence
- Prefer controlled iteration over uncontrolled autonomy
- The Critic acts as an analyst, not an auditor
- Uncertainty is treated as a first-class output
- The Evidence Register is the single source of truth
- Report generation is deterministic and auditable

# Complete Architecture Summary

AIRS is designed around controlled autonomy.

The system does not allow unrestricted AI decision-making.

Instead, it combines:

- Deterministic computation
- Evidence collection
- Provenance tracking
- Specialized agents
- Rule-based quality control
- Human-readable reporting

The architecture ensures that every conclusion can be traced back through:

```text
Report
  │
  ▼
Hypothesis
  │
  ▼
Evidence Register
  │
  ▼
Agent Output
  │
  ▼
Source Data
```

---

# Architectural Philosophy

## Evidence Before Conclusions

Every research conclusion must have supporting evidence.

The system prioritizes:

- Source tracking
- Raw values
- Computation tiers
- Agent ownership
- Data timestamps

---

## Separation of Responsibilities

Each component has a specific role:

| Component | Responsibility |
|---|---|
| Data Layer | Collect and prepare information |
| Database Layer | Store persistent research state |
| Agents | Analyze specialized domains |
| Evidence Register | Store verified research evidence |
| Critic Agent | Evaluate research quality |
| Hypothesis Engine | Convert evidence into structured views |
| Risk Agent | Identify downside factors |
| Report Generator | Produce final research documents |
| Loop Controller | Coordinate the full workflow |

---

# Why This Architecture Works

Traditional AI workflows often follow:

```text
Question → LLM → Answer
```

AIRS follows:

```text
Question
    ↓
Evidence Collection
    ↓
Specialized Analysis
    ↓
Evidence Validation
    ↓
Research Quality Review
    ↓
Structured Hypothesis
    ↓
Professional Report
```

This creates a system that is:

- Explainable
- Auditable
- Reproducible
- Extensible

---

# Future Architecture Extensions

The current architecture supports future additions without changing the foundation.

Potential extensions:

- Audit Trail Layer
- Historical Accuracy Tracking
- Backtesting Infrastructure
- Additional Evidence Sources
- New Research Agents
- Web Interface Layer
- Portfolio Research Workflows

The core architecture remains:

```text
Evidence → Analysis → Critique → Hypothesis → Report
```

---

# Final Architecture Statement

AIRS is not designed to replace analysts.

It is designed to provide a structured research environment where AI systems can:

- Gather evidence
- Analyze information
- Expose uncertainty
- Surface contradictions
- Produce explainable research

The system values:

> Explainability before persuasion.

> Evidence before conclusions.

> Research quality before prediction.

---

# AIRS v0.3.7

## Autonomous Investment Research System

**Evidence-Driven Investment Research Infrastructure**