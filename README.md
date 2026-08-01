# AIRS — Autonomous Investment Research System

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)
![AI](https://img.shields.io/badge/Architecture-Multi--Agent_AI-purple)

> An AI-powered multi-agent investment research platform that automates the workflow of a professional investment research team.

Built with **Python**, **SQLite**, and **local LLMs (Ollama)**.

**Goal:** Produce structured, evidence-based investment research — **not price predictions.**

---

# ✨ Features

- 📊 **Multi-Dimensional Audit Dashboard**
  - Data Quality
  - Coverage
  - Agreement
  - Stability

- 🧭 **Directional Bias + Uncertainty**
  - Raw evidence weighting
  - Explicit uncertainty
  - No artificial probabilities

- 📚 **Evidence Register**
  - Central provenance tracking
  - Source attribution
  - Tier tracking
  - Data point tracking
  - Timestamped evidence

- 🔁 **Adaptive Research Loop**
  - Stops early when evidence is sufficient
  - Avoids unnecessary computation
  - Dashboard-driven iteration

- 🤖 **Local LLM Integration (Ollama)**
  - News summarization
  - Signal extraction
  - Report generation

- 📈 **Quantitative Financial Analysis**
  - Tiered computation
  - 3-month → 6-month → 1-year analysis

- 📰 **Business & News Analysis**
  - RSS ingestion
  - Catalyst extraction
  - Business signal detection

- 🖥️ **Technical Ecosystem Analysis**
  - GitHub activity
  - Repository health
  - Contributor analysis

- ⚠️ **Rule-Based Risk Assessment**
  - Deterministic downside analysis
  - Cross-agent contradiction detection

- 🔍 **6-Phase Critic Agent**

  ```text
  Inventory
      ↓
  Directional Signals
      ↓
  Dashboard
      ↓
  Contradictions
      ↓
  Active Questions
      ↓
  Halt Decision
  ```

- 💰 **Zero API Cost Development**
  - Local-first
  - No paid APIs required

---

# What AIRS Does

Run a single command:

```bash
python main.py --entity AAPL --repo apple/swift --ticker AAPL --hypotheses
```

AIRS automatically performs an investment committee workflow.

---

# Agent Overview

| Agent | Purpose | Uses LLM? | Status |
|-------|---------|-----------|--------|
| 📊 Quant Agent | Returns, volatility, momentum, RSI, MACD, drawdown, risk score, trend | No | ✅ Ready |
| 🖥️ Technical Agent | GitHub commits, contributors, repository health | No | ✅ Ready |
| 📰 Business Agent | News analysis, signals, catalysts, risks | Yes (Ollama) | ✅ Ready |
| ⚠️ Risk Agent | Downside analysis, contradiction detection | No | ✅ Ready |
| 🔍 Critic Agent | 6-phase research director, dashboard-driven halt | No (Rule-based) | ✅ Ready |

---

# Final Outputs

After all agents complete, AIRS generates:

## 📊 Audit Dashboard

A four-dimensional research quality scorecard.

Measures:

- Data Quality
- Coverage
- Agreement
- Stability

---

## 🧭 Directional Bias

Evidence-weighted investment direction.

Unlike traditional AI systems, AIRS reports:

- Bullish strength
- Bearish strength

using **raw evidence weights**, **not percentages**.

---

## ❓ Uncertainty Score

A separate measure of epistemic uncertainty based on:

- Scarcity
- Conflict
- Coverage

---

## 🔍 Active Questions

Specific research gaps that additional evidence could answer.

These are investigative questions—not feature checklists.

---

## ⚠️ Unresolved Contradictions

Cross-dimensional disagreements detected using 12 deterministic rules.

Examples include:

- Positive business signals but declining price
- Oversold RSI with continuing downtrend
- Strong developer activity but weakening fundamentals

---

## 📚 Evidence-Backed Hypotheses

Every investment hypothesis includes:

- Source
- Supporting evidence
- Direction
- Strength

Every claim is traceable to the Evidence Register.

---

# Example Output

```text
============================================================
AIRS EVIDENCE-DRIVEN LOOP 
============================================================

------------------------------------------------------------
PHASE 0: CAPABILITY PROBE
------------------------------------------------------------

✓ Quant available: ticker 'AAPL' resolved
~ Technical: no repo provided, skipping probe

Asset type: public_stock

Available dimensions:
• Quant
• Business

------------------------------------------------------------
PHASE 1: BOOTSTRAP
(Business + Technical)
------------------------------------------------------------

→ Running business analysis for AAPL...

Business: complete (3 signals)
→ Evidence Register

Bootstrap complete.
Register now contains 1 evidence item.

------------------------------------------------------------
PHASE 2: ITERATIVE EVIDENCE ACCUMULATION
------------------------------------------------------------

----------------------------------------
ITERATION 1 / 3
----------------------------------------

→ Quant Tier 1 (3-month depth)

Quant tier upgraded:

• price_data
• returns
• volatility
• momentum
• trend
• risk score
...

→ Running Critic Agent...

==================================================
EVIDENCE AUDIT (Iteration 1)
==================================================

Asset Type:
public_stock

Data Quality:
81%

Coverage:
59%
(10 / 17 features)

Agreement:
High

Positive Dimensions:
0

Negative Dimensions:
2

Neutral Dimensions:
0

Stability:
Unknown
(First iteration)

--------------------------------------------------

Active Questions:
None

--------------------------------------------------

Contradictions:
None

--------------------------------------------------

Decision:
COMPLETE

Reason:
coherent_view

Narrative:

All available dimensions agree.

Deeper analysis is unlikely to change the investment thesis.

==================================================

✅ HALT

All available dimensions agree.

Further iterations are unnecessary.

------------------------------------------------------------
PHASE 3: FINAL OUTPUT GENERATION
------------------------------------------------------------

→ Generating Risk Assessment...

Risk:
HIGH

→ Generating Hypotheses...

============================================================
FINAL RESULTS SUMMARY
============================================================

Entity:
AAPL

Asset Type:
public_stock

Iterations:
1

Halt Reason:
coherent_view

Evidence Collected:
11 items

--------------------------------------------------
AUDIT DASHBOARD
--------------------------------------------------

Data Quality:
81%

Coverage:
59%

Agreement:
High

Stability:
Unknown

--------------------------------------------------
INVESTMENT THESIS
--------------------------------------------------

Directional Bias:
BEARISH

Bullish Strength:
0.58

Bearish Strength:
1.68

Net Score:
-1.10

--------------------------------------------------

Uncertainty:
Moderate (29%)

Scarcity:
0.07

Conflict:
0.14

Coverage:
0.08

--------------------------------------------------
ACTIVE QUESTIONS
--------------------------------------------------

None

--------------------------------------------------
UNRESOLVED CONTRADICTIONS
--------------------------------------------------

None

--------------------------------------------------
RISK ASSESSMENT
--------------------------------------------------

Overall Risk:
HIGH

Risks:
3

Warnings:
1

============================================================
INVESTMENT HYPOTHESES
============================================================

BULL CASE

Strength:
0.58

• RSI oversold
• Positive business signals

--------------------------------------------------

BEAR CASE

Strength:
1.68

• Downtrend
• -13.8% monthly decline
• High risk score
• Negative business signals

--------------------------------------------------

BASE CASE

Moderate risk profile

============================================================

Generated from:
11 evidence items

Dimensions used:

• Quant
• Business

============================================================
```
# Architecture

```text
                    User Request
                         │
                         ▼
            Research Controller
               (Loop Engine)
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
      Quant         Technical        Business
      Agent           Agent           Agent
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
              Evidence Register
              (core/evidence.py)
                         │
                         ▼
                  Critic Agent
                (6-Phase Analyst)
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
      More Research         Hypothesis Engine
   (if contradictory)    (Directional Bias +
                            Uncertainty)
                                   │
                                   ▼
                             Risk Agent
                           (Legacy Bridge)
                                   │
                                   ▼
                              Final Output
                    (Dashboard + Hypotheses)
```

> **Key Architectural Principle**
>
> - The **Critic Agent** is **100% rule-based**.
> - No LLM decides what to compute or when to halt.
> - The **Evidence Register** is the single source of truth.
> - Investment hypotheses are **evidence-weighted**, **not probability-normalized**.

---

# Project Structure

```text
AIRS/
│
├── agents/
│   ├── quant.py              # Tiered numerical analysis (3mo → 6mo → 1y)
│   ├── technical.py          # GitHub ecosystem health
│   ├── business.py           # RSS news + Ollama summarization
│   ├── risk.py               # Rule-based downside analysis
│   └── critic.py             # 6-phase research director
│
├── controller/
│   └── loop.py               # Evidence-driven loop controller
│
├── core/
│   └── evidence.py           # Evidence Register (single source of truth)
│
├── data/
│   ├── db.py                 # SQLite database layer
│   └── fetcher.py            # yfinance wrapper with retry logic
│
├── reports/
│   ├── hypothesis.py         # Directional Bias + Uncertainty engine
│   └── generator.py          # Report Generator (Issue #10)
│
├── utils/
│   └── ollama_client.py      # Ollama client with retry logic
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── CONTEXT.md
│   ├── CURRENT_TASK.md
│   ├── DECISIONS.md
│   ├── LEARNING.md
│   ├── MEMORY.md
│   ├── ROADMAP.md
│   ├── SETUP.md
│   └── SPEC.md
│
├── tests/
│
├── main.py                   # CLI entry point
├── requirements.txt
└── README.md
```

---

# 🚀 Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/deadpool-kha/AIRS.git

cd AIRS
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install Ollama

Download and install Ollama:

https://ollama.com

---

### Pull the Default Model

```bash
ollama pull qwen2.5:7b
```

---

### Start the Ollama Server

```bash
ollama serve
```

Keep the Ollama server running in a separate terminal while using AIRS.

---

# 💻 Usage

## Quant Analysis (Single Shot)

```bash
python main.py --entity AAPL --quant-only
```

---

## Technical Analysis

```bash
python main.py --repo bitcoin/bitcoin --technical-only
```

---

## Business Analysis

```bash
python main.py --entity NVIDIA --business-only
```

---

## Full Evidence-Driven Research Loop

### Public Stock

```bash
python main.py \
    --entity AAPL \
    --ticker AAPL \
    --hypotheses
```

---

### Cryptocurrency with Repository

```bash
python main.py \
    --entity BTC-USD \
    --repo bitcoin/bitcoin \
    --ticker BTC-USD \
    --hypotheses
```

---

### Stock with GitHub Repository

```bash
python main.py \
    --entity AAPL \
    --repo apple/swift \
    --ticker AAPL \
    --hypotheses
```

---

## Show Evidence Source Tracking

```bash
python main.py \
    --entity AAPL \
    --quant-only \
    --show-sources
```

---

# ⚙️ Command Line Arguments

| Argument | Description |
|-----------|-------------|
| `--entity` | Company or asset name (e.g., `AAPL`, `Bitcoin`) |
| `--ticker` | Stock or crypto ticker for quantitative analysis |
| `--repo` | GitHub repository in `owner/repo` format |
| `--quant-only` | Run only the Quant Agent |
| `--technical-only` | Run only the Technical Agent |
| `--business-only` | Run only the Business Agent |
| `--hypotheses` | Run the complete evidence-driven research loop |
| `--show-sources` | Display evidence provenance and source tracking |
| `--period` | Quant analysis period (`1mo`, `3mo`, `6mo`, `1y`) |

> **Note**
>
> `--risk-only` and `--critic` standalone flags have been deprecated.
>
> Risk analysis and Critic evaluation execute automatically during the `--hypotheses` workflow.

# 📊 Current Development Status

**Current Version:** `v0.3.6`

---

# ✅ Completed

### Data Foundation

- SQLite database
- `yfinance` fetcher
- Retry logic with exponential backoff

---

### Quant Agent v3

- Tiered computation
  - 3 months
  - 6 months
  - 1 year
- Returns
- Volatility
- Momentum
- RSI
- MACD
- Drawdown
- Risk score

---

### Technical Agent

- GitHub REST API integration
- Repository health analysis
- Contributor activity
- Commit analysis

---

### Business Agent

- RSS news ingestion
- Ollama summarization
- Signal extraction
- Catalyst detection

---

### Risk Agent

- Rule-based downside analysis
- Cross-agent contradiction detection
- Blind-spot warnings

---

### Critic Agent v2

- 6-phase analyst model
- Dashboard-driven evaluation
- Iteration-aware stopping logic

---

### Evidence Register

- Central provenance tracking
- Single source of truth
- Trustworthiness metadata

---

### Hypothesis Engine v3

- Directional Bias
- Explicit Uncertainty
- Evidence-backed claims

---

### Loop Controller v2

- Bootstrap workflow
- Iterative evidence accumulation
- Dashboard history
- Early stopping

---

# 🚧 In Progress

## Report Generator (Issue #10)

Generate professional investment memos in:

- Markdown
- PDF

Inputs:

- Audit Dashboard
- Evidence Register
- Investment Hypotheses

---

# 📅 Planned

- Streamlit Web Interface
- FastAPI Backend
- Portfolio Analysis
- Multi-company Comparison

---

# 🎯 Key Features

## 🏠 Local-First AI

Everything runs locally.

- No OpenAI API required
- No paid APIs
- Low operating cost
- Ollama runtime

---

## 📊 Deterministic Financial Analysis

Financial calculations **never** rely on an LLM.

Computed using Python and pandas:

- Returns
- Volatility
- Drawdown
- RSI
- MACD
- Trend detection
- Risk metrics

---

## 🧭 Directional Bias + Uncertainty

Instead of artificial probabilities such as:

```text
Bull: 38%
Bear: 25%
Base: 37%
```

AIRS reports two independent dimensions.

### Directional Bias

Evidence-weighted investment direction.

Measures:

- Bullish strength
- Bearish strength

Based entirely on evidence.

---

### Uncertainty

A separate score computed from:

- Scarcity
- Conflict
- Coverage

---

### Base Case

Contains only neutral evidence.

It is **not** a leftover probability.

---

## 🔁 Adaptive Loop Engineering

The research loop asks different questions at each iteration.

### Iteration 1

> Can I form a coherent directional view?

### Iteration 2

> Did deeper data change the story?

### Iteration 3

> Circuit breaker

Most assets stop after **Iteration 1**.

Only contradictory or unclear cases proceed further.

---

## 🔍 6-Phase Critic Agent

The Critic evaluates research quality through six stages.

1. **Inventory**
   - Catalog available evidence

2. **Directional Signals**
   - Bullish
   - Bearish
   - Neutral

3. **Dashboard**
   - Data Quality
   - Coverage
   - Agreement
   - Stability

4. **Contradictions**
   - 12 hardcoded cross-agent rules
   - Catch-all validation

5. **Active Questions**
   - Investigative questions
   - Not feature checklists

6. **Halt Decision**
   - Iteration-aware stopping logic

---

## 📚 Evidence Register

The single source of truth.

Every agent:

- Reads from it
- Writes to it

Every investment claim references it.

### Provenance Tracking

Each evidence item stores:

- Source agent
- Computation tier
- Data points
- Data period
- Timestamp

---

## ⚠️ Cross-Agent Validation

AIRS contains **12 deterministic contradiction rules** that detect conflicts between research dimensions.

Example contradictions include:

- Price rising while fundamentals deteriorate
- RSI oversold but trend remains bearish
- High developer activity with declining adoption
- Hype versus actual delivery
- Strong news sentiment despite worsening quantitative metrics

# 📖 Documentation

| File | Description |
|------|-------------|
| `ARCHITECTURE.md` | Complete system architecture and component design |
| `CHANGELOG.md` | Version history and release notes |
| `CONTEXT.md` | AI assistant context and current project state |
| `CURRENT_TASK.md` | Active development tracker |
| `DECISIONS.md` | Engineering decision log |
| `LEARNING.md` | Knowledge capture and implementation notes |
| `MEMORY.md` | Long-term project memory for AI assistants |
| `ROADMAP.md` | Phase-based development roadmap |
| `SETUP.md` | Installation, setup, and troubleshooting |
| `SPEC.md` | Product specification and data models |

---

# 📈 Current Progress

| Component | Status |
|-----------|--------|
| Data Layer | ✅ Complete |
| Quant Agent | ✅ Complete |
| Technical Agent | ✅ Complete |
| Business Agent | ✅ Complete |
| Risk Agent | ✅ Complete |
| Critic Agent | ✅ Complete |
| Evidence Register | ✅ Complete |
| Hypothesis Engine | ✅ Complete |
| Loop Controller | ✅ Complete |
| Report Generator | 🚧 In Progress |
| Web Interface | 📅 Planned |

---

# 🗺️ Roadmap

## ✅ Phase 1 — Data Foundation

- SQLite database
- Market data fetcher
- Data persistence
- Retry logic

---

## ✅ Phase 2 — Quant Agent

- Tiered computation
- Returns
- Volatility
- Momentum
- RSI
- MACD
- Drawdown
- Risk score

---

## ✅ Phase 3 — Technical Agent

- GitHub REST API integration
- Commit analysis
- Contributor metrics
- Repository health score

---

## ✅ Phase 4 — Business Agent

- RSS ingestion
- Ollama summarization
- Signal extraction
- Catalyst detection

---

## ✅ Phase 5 — Risk Agent

- Downside analysis
- Cross-agent contradiction detection
- Blind-spot warnings

---

## ✅ Phase 6 — Critic Agent

- 6-phase analyst model
- Dashboard-driven evaluation
- Iteration-aware stopping logic

---

## ✅ Phase 7 — Loop Controller

- Bootstrap workflow
- Iterative evidence accumulation
- Dashboard history
- Early stopping

---

## 🚧 Phase 8 — Report Generator

Generate professional investment research reports using:

- Audit Dashboard
- Evidence Register
- Risk Assessment
- Investment Hypotheses

Planned output formats:

- Markdown
- PDF

---

## 📅 Future Work

- FastAPI backend
- Streamlit dashboard
- Portfolio analysis
- Multi-company comparison
- Additional data providers

---

# 🏗️ Design Principles

The project follows several core engineering principles.

## 📚 Evidence Over Opinions

Every conclusion must be traceable to the **Evidence Register**.

No unsupported claims.

---

## 📊 Deterministic Calculations

Whenever possible, calculations are implemented using traditional programming.

Never use an LLM for:

- Financial calculations
- Statistics
- Metrics
- Database operations

---

## 🤖 Use LLMs Where They Add Value

LLMs are reserved for tasks requiring qualitative reasoning, including:

- News summarization
- Signal extraction
- Planning
- Report writing
- Suggestions

---

## 🧭 Explicit Uncertainty

Uncertainty is treated as a first-class output.

It is reported separately from directional conviction.

---

## 🔍 The Critic Is an Analyst

The Critic Agent asks research questions.

It does **not** behave like an auditor or checklist engine.

---

## 💰 Local-First Development

The system is designed to operate with:

- Local LLMs
- Free data sources
- Near-zero operating cost

---

# 🎓 What This Project Demonstrates

AIRS was built as a portfolio project showcasing practical AI engineering skills.

Key areas include:

- Multi-Agent AI Systems
- Agent Orchestration
- Loop Engineering
- Evidence-Based Research Workflows
- Quantitative Financial Analysis
- Local LLM Integration (Ollama)
- Python Software Engineering
- SQLite Database Design
- GitHub API Integration
- RSS Data Processing
- Software Architecture
- Engineering Decision Logging

---

# 🔬 Research Philosophy

Unlike many AI investment tools that produce a single opinion, AIRS follows an **investment committee** approach.

Each agent specializes in a different research domain.

Rather than relying on a single model, AIRS:

1. Collects evidence from multiple independent sources.
2. Stores evidence in the Evidence Register.
3. Validates research quality using the 6-phase Critic.
4. Identifies contradictions and research gaps.
5. Produces competing investment hypotheses.
6. Reports explicit uncertainty.

The system **does not predict prices**.

Instead, it organizes publicly available information into structured, auditable investment research.

---

# ⚠️ Current Limitations

Current limitations include:

- Report Generator is not yet implemented (`NotImplementedError`)
- Business Agent reuses the same RSS feed during later iterations (live news only)
- Technical Agent reuses the same GitHub snapshot between iterations
- Only the Quant Agent benefits from deeper data across iterations
- Risk Agent still reads from the Evidence Register through a legacy compatibility bridge
- Hypothesis strength thresholds are intuitive and have not yet been validated against historical datasets

---

# 🤝 Contributing

Contributions are welcome.

Whether you want to report bugs, suggest features, improve documentation, or submit code, your help is appreciated.

## Development Workflow

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

Please keep pull requests focused and well documented.

---

# 📄 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.

---

# ⚠️ Disclaimer

AIRS is an educational and research project.

It **does not provide financial advice** and should **not** be used as the sole basis for investment decisions.

The system organizes publicly available information into structured research reports, but all investment decisions should be supported by independent research and professional judgment.

---

# ⭐ Support the Project

If you found AIRS interesting or useful, consider giving the repository a **star** on GitHub.

It helps others discover the project and supports continued development.

---

## Built With

- 🐍 Python
- 🗄️ SQLite
- 🤖 Ollama
- 📊 pandas
- 📈 NumPy
- 🌐 GitHub REST API
- 📰 RSS Feeds

---

**AIRS — Autonomous Investment Research System**

*Evidence-driven. Transparent. Local-first.*