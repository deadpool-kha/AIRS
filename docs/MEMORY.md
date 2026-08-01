# MEMORY.md

# Project: Autonomous Investment Research System (AIRS)

---

# Role of This Document

This document provides complete project context for AI assistants and developers.

When assisting with this project:

- Understand the architecture before suggesting changes.
- Do not redesign the system unless explicitly requested.
- Prefer simple and reliable engineering solutions.
- Explain tradeoffs behind technical decisions.
- Prioritize completing the MVP.

---

# Project Goal

Build an AI-powered investment research system that automates the workflow of a professional investment research team.

The system analyzes:

## 1. Public Companies

Examples:

- NVIDIA
- Tesla

## 2. Crypto Protocols / Assets

Examples:

- Ethereum
- Solana
- Stacks

## 3. AI Companies / Startups

Using publicly available information.

---

## Important Goal Clarification

The goal is **NOT** to predict stock or crypto prices.

The goal is to create:

- Structured research
- Evidence-based analysis
- Professional investment reports

---

# Why This Project Exists

This project is being built as:

1. A portfolio project for AI/software engineering roles.
2. A demonstration of modern AI engineering skills.
3. A practical exploration of investment research automation.

The project combines:

- AI agents
- Loop engineering 
- Quantitative analysis
- Data engineering
- Financial research workflows

---

# Core Product Vision

## User Input

Example:

> Analyze NVIDIA

The system performs an investment committee workflow.

---

## Research Workflow

```text
1. Collect evidence
        ↓
2. Write evidence to Evidence Register
        ↓
3. Analyze data
   - Quant
   - Technical
   - Business
        ↓
4. Evaluate risks
        ↓
5. Critique research quality
   (6-phase analyst model)
        ↓
6. Iterate if unclear or contradictory
        ↓
7. Generate competing hypotheses
   (Directional Bias + Uncertainty)
        ↓
8. Generate final research memo
```

---

# Important Engineering Principle

## Do NOT Use LLMs For Everything

Traditional programming handles:

- Calculations
- Metrics
- Data processing
- Database operations
- Deterministic analysis
- Feature selection
- Halt decisions

---

## LLM Responsibilities

LLMs are used for:

- Planning
- Qualitative reasoning
- Critique suggestions
- Summarization
- Final report generation

---

## Critical Rule

The LLM is a reasoning layer, not the entire system.

The Critic Agent is:

```
100% rule-based
```

No LLM decides:

- What features to compute
- When to halt
- Confidence scores

LLM suggestions are:

- Display-only
- Non-binding

---

# High-Level Architecture

```text
                     User
                      │
                      │
              Research Request
                      │
                      ▼
            Research Controller
              (Loop Engine)
                      │
    ┌──────────┬──────────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼
 Quant    Technical   Business     Risk
 Agent      Agent       Agent      Agent
    │          │          │          │
    └──────────┴──────────┴──────────┘
                      │
                      ▼
          Evidence Register
          (core/evidence.py)
                      │
                      ▼
               Critic Agent
              (6-phase analyst)
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
 More Research              Hypothesis Engine
(if unclear or              (Directional Bias
 contradictory)              + Uncertainty)
                                  │
                                  ▼
                            Final Report
```

---

# Core Components

---

# 1. Data Layer

Responsible for collecting external information.

---

## Market Data

Sources:

- Yahoo Finance (`yfinance`)
- CoinGecko

Collected data:

- Price
- Volume
- Returns
- Volatility

---

## Technical Data

Source:

- GitHub API

Collected data:

- Commits
- Contributors
- Releases
- Issues

---

## Business Data

Sources:

- RSS feeds
- Company websites
- Public announcements

Collected data:

- Partnerships
- Funding
- Product launches
- Important events

---

# 2. Database Layer

## Initial Database

```
SQLite
```

## Future Possibility

```
PostgreSQL
```

## Stores

- Entities
- Market data
- GitHub activity
- News
- Research results
- Agent states
- Loop iteration history
- Dashboard snapshots

---

# 3. Evidence Register

Location:

```text
core/evidence.py
```

Central in-memory evidence accumulator.

---

## Design

- Plain Python dictionary
- `EvidenceItem` dataclasses
- Provenance tracking:
  - Source agent
  - Tier
  - Data points
  - Data period
  - Timestamp

Trustworthiness checks:

- Minimum data points
- Statistical validity checks

No:

- Database dependency
- Microservices

---

## API

```python
add(
    key,
    value,
    source,
    tier,
    data_points,
    data_period
)

get(key)

has(key)

get_meta(key)

is_trustworthy(
    key,
    min_data_points
)

snapshot()

list_by_source(source)

list_by_tier(tier)
```

---

# 4. Agents

Agents are specialized modules.

They are **not** separate ChatGPT conversations.

All agents:

- Read from Evidence Register
- Write outputs to Evidence Register

---

# Quant Agent

## Purpose

Analyze numerical information.

## Responsibilities

- Price trends
- Returns
- Volatility
- Momentum
- Drawdown
- Risk metrics
- RSI
- MACD
- ATR
- Beta
- Correlation matrix

---

## Implementation

Python libraries:

- pandas
- numpy
- Statistics libraries

No LLM required.

---

## Tiered Computation

### Tier 1 (3 Months)

Basic features.

### Tier 2 (6 Months)

Adds:

- RSI
- MACD
- Volume profile

### Tier 3 (1 Year)

Adds:

- ATR
- Volatility regime
- Beta
- Correlation

---

# Technical Agent

## Purpose

Analyze technical ecosystem health.

## Data Source

GitHub activity.

## Metrics

- Contributor growth
- Commit frequency
- Release activity
- Project maintenance

## Implementation

Python.

May use LLM for summary generation only.

Runs once per session during bootstrap.

---

# Business Agent

## Purpose

Analyze qualitative business information.

## Inputs

- News
- Announcements
- Public information

Uses local LLM for:

- Summarization
- Signal extraction

Runs once per session during bootstrap.

---

# Risk Agent

## Purpose

Identify weaknesses and negative signals.

Examples:

- Competition
- Regulatory concerns
- Declining activity
- High-risk factors

Uses:

- Rules
- Data analysis

Reads from Evidence Register through legacy bridge.

---

# Critic Agent

## Purpose

Evaluate research quality and direct inquiry.

---

# Architecture: 6-Phase Pipeline

## 1. Inventory

Catalog available evidence.

## 2. Directional Signals

Extract:

- Bullish
- Bearish
- Neutral

signals per dimension.

## 3. Dashboard

Compute four auditable dimensions:

- Data Quality
- Coverage
- Agreement
- Stability

## 4. Contradictions

Execute 12 hardcoded cross-agent rules.

## 5. Active Questions

Generate specific research questions.

## 6. Halt Decision

Iteration-aware stopping logic.

---

## Technology

Decision system:

```
100% rule-based
```

Optional LLM:

- Qualitative suggestions only
- Display-only
- Non-binding

---

# 5. Hypothesis Engine

Location:

```text
reports/hypothesis.py
```

Generates investment hypotheses from the Evidence Register.

---

## Output

### Directional Bias

Bullish strength versus bearish strength.

Uses:

```
Raw evidence weights
```

---

### Uncertainty

Separate score based on:

- Scarcity
- Conflict
- Coverage

---

### Claims

Each claim contains:

- Source
- Raw value
- Strength
- Description
- Direction

---

### Base Case

Neutral signals.

Not:

```
Leftover probability
```

---

## Design Principles

- No artificial probability floors
- No normalization to 100%
- Every claim traceable to Evidence Register
- Uncertainty is explicit

---

# 6. Loop Engineering Design

The system uses a controlled research loop engineering concept.

---

# Research Loop

```text
Receive Goal
      │
      ▼
Capability Probe
(detect available dimensions)
      │
      ▼
Bootstrap
(Business + Technical run ONCE)
      │
      ▼
Evidence Register
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
(coherent view?)
      │
      ▼
Iteration 2
Quant Tier 2
      │
      ▼
Critic
(stable thesis?)
      │
      ▼
Iteration 3
Quant Tier 3
      │
      ▼
Critic
(circuit breaker)
      │
      ▼
Final Output
Risk + Hypotheses
      │
      ▼
Report Generator
(future)
```

---

# Loop Controller Decisions

Business and Technical:

```
Run once
```

Reason:

Their inputs do not change during execution.

Quant:

```
Only iterative agent
```

---

## Halt Conditions

Stop when:

- Dimensions agree on direction
- Hypotheses stabilize
- Active questions cannot be answered by deeper data
- `MAX_ITERATIONS = 3`

---

# 7. LLM Architecture

Local-first approach.

No paid APIs during development.

---

## Runtime

```
Ollama
```

---

## Supported Models

- Qwen 2.5 7B
- Llama 3.1 8B
- Mistral 7B

---

# LLM Responsibilities

Used for:

- Planning
- Qualitative reasoning
- Critique suggestions
- Report writing
- News summarization
- Signal extraction

---

# LLM Is NOT Used For

Never use LLMs for:

- Calculations
- Metrics
- Database operations
- Feature selection
- Halt decisions
- Confidence scores

---

# Hardware Environment

| Component | Specification |
|---|---|
| GPU | NVIDIA GTX 1060 6GB |
| RAM | 16 GB |
| OS | Windows 10 |
| Development Cost | $0 |

---

# Technology Stack

| Category | Technology |
|---|---|
| Backend | Python |
| Database | SQLite |
| AI Runtime | Ollama |
| Vector Search | FAISS / ChromaDB (future) |
| Frontend | Streamlit (future) |

---

# Development Rules

- Build the smallest working version first.
- Avoid unnecessary complexity.
- Do not build a generic chatbot.
- Do not add agents without a clear purpose.
- Document important decisions.
- Keep architecture stable.
- Prefer working software over theoretical design.
- Critic remains rule-based.
- Never let LLM decide computation or halting.
- Uncertainty must remain explicit.

---

# Git Workflow

Rules:

- All work happens on feature branches.

Example:

```text
feature/quant-agent
```

- No commits directly to main without PR review.
- Issues track:
  - Bugs
  - Features
  - Research tasks

Close issues with commit messages:

```text
Fixes #7
```

Make:

- Small commits
- Frequent commits
- Descriptive messages

---

# Current Project Status

## Stage

```
Active Development — Core Loop Complete
```

---

## Completed

✅ Project concept defined  
✅ Architecture designed  
✅ Documentation system created  
✅ GitHub repository initialized  
✅ Database foundation  
✅ All 5 agents:
- Quant
- Technical
- Business
- Risk
- Critic

✅ Evidence Register  
✅ Hypothesis Engine v3  
✅ Loop Controller v2  

---

# Current Priorities

1. Report Generator (Issue #10)
2. Risk Agent direct Evidence Register integration

---

# Success Criteria

The MVP is successful if:

- A user can analyze an entity.
- The system collects real data.
- Agents produce structured analysis.
- The loop evaluates research quality using a dashboard.
- The system generates competing hypotheses.
- Directional bias and uncertainty are explicit.
- The system generates a professional investment memo.
- The project demonstrates modern AI engineering practices.
- Every output is traceable to evidence in the Evidence Register.