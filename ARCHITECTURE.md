# ARCHITECTURE.md

# Autonomous Investment Research System (AIRS)

## Purpose

This document explains the technical architecture of the system.

The goal is to build a modular AI research platform that collects information, analyzes evidence, evaluates research quality, and generates professional investment research reports.

---

# System Overview

The system consists of five major layers.

```text
             User
              |
              |
       Research Request
              |
              v

   Research Controller Layer
        (Loop Engine)
              |
   --------------------------------
   |              |               |
   v              v               v
External      Analysis       LLM Reasoning
 Sources       Modules        Components
              |
              v
      Report Generator
              |
              v
      Investment Memo
```

---

# Layer 1: Data Layer

Responsible for collecting and storing information.

## Data Sources

- Yahoo Finance (`yfinance`)
- GitHub API
- RSS feeds
- Public documents

## Responsibilities

- Data collection
- Data cleaning
- Data normalization
- Data storage

---

# Layer 2: Database Layer

## Initial Database

- SQLite

## Stores

- Entities
- Historical market data
- Technical activity
- News
- Research states
- Reports
- Loop iteration history

---

# Layer 3: Agent Layer

Agents are specialized analysis modules.

---

## Quant Agent

### Purpose

Handles numerical analysis.

### Input

- Market data

### Output

- Trend analysis
- Volatility
- Momentum
- Risk metrics

### Technology

- Python
- pandas
- numpy

No LLM required.

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

---

## Business Agent

### Purpose

Analyzes business activity.

### Input

- News
- Public information

### Output

- Business catalysts
- Business signals

### Technology

- Python
- Ollama (for summarization)

---

## Risk Agent

### Purpose

Identifies weaknesses and potential risks.

### Output

- Risk factors
- Concerns
- Areas of uncertainty

### Technology

- Rule-based analysis
- Data analysis
- LLM reasoning when appropriate

---

## Critic Agent

### Purpose

Evaluates overall research quality.

### Input

- Outputs from all analysis agents

### Output

- Quality assessment
- Identified evidence gaps
- Recommendations for additional research

### Technology

- Ollama (reasoning)

---

# Layer 4: Loop Controller

The Loop Controller manages workflow execution using loop engineering principles.

## Responsibilities

- Maintain workflow state
- Decide the next action
- Track research completion
- Invoke required agents
- Manage research iterations (maximum of 3)

## Workflow

```text
Goal
  ↓
Planning
  ↓
Research
  ↓
Analysis
  ↓
Evaluation (Critic)
  ↓
Decision:
Iterate or Complete
  ↓
Completion
```

---

# Layer 5: LLM Layer

## LLM Responsibilities

- Planning
- Reasoning
- Critique
- Report writing

## LLMs Are NOT Used For

- Calculations
- Simple data processing
- Database operations

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
| LLM unavailable | Fall back to rule-based analysis and reduce confidence score |
| Database locked | Wait 1 second, retry, then fail gracefully if unsuccessful |
| GitHub rate limit | Use unauthenticated fallback where possible and flag data limitations |

---

# Design Principles

1. Modular components
2. Local-first development
3. Minimize API costs (target: **$0**)
4. Produce human-readable outputs
5. Base conclusions on evidence
6. Prefer controlled iteration over uncontrolled autonomy