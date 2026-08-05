# AIRS — Autonomous Investment Research System

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)
![Version](https://img.shields.io/badge/Version-0.3.7-blueviolet)

> **Evidence-Driven Investment Research Infrastructure**
>
> Not an AI stock predictor. Not a trading bot. A structured research engine that collects evidence, audits its own reasoning, and tells you exactly what it knows — and what it doesn't.

Built with **Python**, **SQLite**, **Ollama**, and **yfinance**.  
Runs entirely local. Zero API cost.

---

# What AIRS Actually Does

You run one command. AIRS runs an entire investment committee workflow:

```bash
python main.py --entity AAPL --ticker AAPL --repo apple/swift --hypotheses --pdf
```

## What happens:

### Capability Probe

Detects which research dimensions are available:

- Quant
- Technical
- Business

---

### Bootstrap

Runs initial research:

- Business Agent reads news.
- Technical Agent reads GitHub.
- Both agents run once and populate the Evidence Register.

---

### Iterative Quant Analysis

The Quant Agent progressively increases research depth:

```
Tier 1 → 3 months
Tier 2 → 6 months
Tier 3 → 1 year
```

After every tier:

```
Quant Analysis
      ↓
Critic Audit
      ↓
Decision
```

The system only collects more data when evidence quality requires it.

---

### Critic Audit

The Critic Agent performs a 6-phase rule-based evaluation after every iteration.

It evaluates:

- Data quality
- Coverage
- Agreement
- Stability
- Contradictions
- Remaining research gaps

---

### Halt Decision

AIRS does not always run maximum depth.

It stops early when:

- Evidence is coherent
- Contradictions are resolved
- The research objective is satisfied

It continues when:

- Important evidence is missing
- Signals disagree
- More research can improve confidence

---

### Hypothesis Engine

Generates:

- Bull Case
- Bear Case
- Base Case

using:

- Evidence weights
- Directional bias
- Explicit uncertainty

It does **not** generate fake probabilities.

---

### Risk Assessment

Runs deterministic downside analysis:

- Risk severity
- Contradictions
- Warning signals
- Evidence sources

---

### Investment Memo

Generates a professional 7-section research report:

- Markdown output
- Optional PDF export

---

# Live Example: Apple (AAPL)

## 3 Iterations — Full Research Depth

```
╔══════════════════════════════════════════════╗
║  AIRS  v0.3.7                                ║
║  Evidence-Driven Investment Research          ║
╚══════════════════════════════════════════════╝


AIRS Evidence-Driven Loop  |  AAPL


PHASE 0: Capability Probe

OK Quant      ticker 'AAPL' resolved

OK Technical  repo 'apple/swift' found

-> Asset type  public_stock_with_repo



PHASE 1: Bootstrap (Business + Technical)

OK Business  2 signals -> Evidence Register

OK Technical  complete -> Evidence Register



PHASE 2: Iterative Evidence Accumulation


ITERATION 1/3

> Quant Tier 1  3mo data depth

> Critic  evaluating evidence...


┌─ Audit Dashboard ───────────────────────────┐
│ Data Quality  ████████████████░░░░  78%     │
│ Coverage      ████████████░░░░░░░░  61%     │
│ Agreement     LOW                            │
│ Stability     UNKNOWN                        │
└──────────────────────────────────────────────┘


Decision: NEED_MORE_DATA  |  insufficient_clarity



ITERATION 2/3

> Quant Tier 2  6mo data depth


Decision: NEED_MORE_DATA  |  unresolved_questions



ITERATION 3/3

> Quant Tier 3  1y data depth


✓ HALT — max_iterations

Circuit breaker hit. Returning best available analysis.



PHASE 3: Final Output Generation


> Risk Assessment  analyzing...

OK Risk  HIGH


> Hypotheses generating...


> Report generating investment memo...


OK Report saved

reports/output/AAPL_20260805_043449.md



OK Loop Complete

3 iteration(s)

19 evidence items

max_iterations
```

---

# The Report You Get

AIRS generates a professional 7-section investment memo.

The generated report contains:

1. Executive Summary
2. Audit Dashboard
3. Investment Thesis
4. Evidence Register Summary
5. Risk Assessment
6. Active Questions & Unresolved Contradictions
7. Appendix

---

# 1. Executive Summary

Example:

```
Directional Bias: BEARISH

The evidence supports a cautious or negative investment thesis.


Uncertainty Level:

17% — Low


Research loop halted after 3 iterations because:

Circuit breaker: maximum iterations reached.
```

---

# 2. Audit Dashboard

Four independent quality dimensions.

This is **not** a fake confidence percentage.

| Dimension | Score | Details |
|---|---|---|
| Data Quality | 78% | Quant, business, technical |
| Coverage | 100% | 18/18 features present |
| Agreement | Low | 1 positive, 1 negative, 2 neutral |
| Stability | Stable | No dimension flipped direction |

---

# 3. Investment Thesis

## Directional Bias

```
Bullish Strength: 1.21 (3 claims)

Bearish Strength: 2.91 (6 claims)

Net Score: -1.70 → BEARISH
```

---

# Bull Case

| Evidence | Source | Strength | Raw Value |
|---|---|---:|---|
| Low beta (0.77) — defensive growth profile | quant | 0.35 | 0.7719 |
| 2 catalyst(s) identified | business | 0.41 | 2 |
| High development activity: 175.0/week | technical | 0.45 | 175.0 |

---

# Bear Case

| Evidence | Source | Strength | Raw Value |
|---|---|---:|---|
| Price in downtrend | quant | 0.60 | downtrend |
| MACD bearish crossover — momentum turning negative | quant | 0.70 | bearish_crossover |
| Significant drawdown: 13.8% | quant | 0.50 | 0.138 |
| Elevated volatility regime | quant | 0.45 | elevated |
| 1 negative business signal(s) | business | 0.25 | 1 |
| 2 business risks identified | business | 0.41 | 2 |

---

# Base / Neutral Case

| Evidence | Source | Strength | Raw Value |
|---|---|---:|---|
| RSI 45.1 in neutral zone — no clear directional bias | quant | 0.30 | 45.08 |
| Moderate risk profile: 0.30 | quant | 0.35 | 0.3043 |
| Moderate ecosystem health (health: 0.70) | technical | 0.30 | 0.7 |

---

# Uncertainty Analysis

| Factor | Value | Meaning |
|---|---:|---|
| Scarcity | 0.00 | Sufficient evidence volume |
| Conflict | 0.17 | Minor disagreement across dimensions |
| Coverage | 0.00 | All available dimensions active |

> Key design principle:
>
> Directional bias and uncertainty are independent.
>
> Strong conviction can coexist with high uncertainty.
>
> Weak conviction can have low uncertainty.

---

# 4. Evidence Register Summary

## Evidence by Source

| Source | Items |
|---|---|
| Business | 1 item: business_context |
| Technical | 1 item: technical_context |
| Quant | 17 items: price_data, returns, volatility, momentum, moving_averages, drawdown, risk_score, trend, current_price, data_points, rsi, macd, volume_profile, atr, volatility_regime, beta, correlation_matrix |

---

## Evidence by Tier

| Tier | Items |
|---|---|
| Tier 1 (3mo) | 9 items: returns, volatility, momentum, moving_averages, drawdown, risk_score, trend, current_price, data_points |
| Tier 2 (6mo) | 3 items: rsi, macd, volume_profile |
| Tier 3 (1yr) | 5 items: price_data, atr, volatility_regime, beta, correlation_matrix |

---

# Quantitative Evidence

| Metric | Value |
|---|---|
| Returns | daily_mean: 0.1841, weekly: -8.31%, monthly: 0.09% |
| Volatility | 25.85% |
| Momentum (20d) | -1.20% |
| Max Drawdown | 13.80% |
| Risk Score | 0.30 |
| Trend | downtrend |
| RSI | 45.08 |
| MACD | bearish_crossover |
| Beta | 0.77 |
| ATR | 9.90 |

---

# Business Evidence

| Type | Category | Description |
|---|---|---|
| NEUTRAL | Dividend | Apple is set to pay dividends next week... |
| NEGATIVE | Competition | Memory chip inflation may impact Apple's costs... |

### Catalysts

- Apple's upcoming dividend payment
- Outcome of trade secrets lawsuit against OpenAI

### Risks

- Memory chip inflation
- Significant market cap losses following earnings dip

---

# Technical Evidence

| Metric | Value |
|---|---|
| Health Score | 0.70 |
| Commit Frequency | 175.0/week |
| Contributors | 30 |
| Open Issues | 9,161 |
| Days Since Commit | 0 |

---

Every claim traces back to:

- Source
- Tier
- Raw value

Provenance is not optional.

---

# 5. Risk Assessment

```
Overall Risk Level: HIGH

Risks Identified: 4

Warnings: 1

High Severity: 2
```

---

| Severity | Category | Description | Source |
|---|---|---|---|
| HIGH | Momentum | Negative price trend: downtrend | quant_agent |
| HIGH | Competition | Memory chip inflation may impact costs | business_agent |
| MEDIUM | Business | Memory chip inflation impacting costs | business_agent |
| MEDIUM | Business | Significant market cap losses following earnings dip | business_agent |

---

| Severity | Category | Description | Source |
|---|---|---|---|
| MEDIUM | Volatility | Elevated risk score: 0.30 | quant_agent |

---

# 6. Active Questions & Unresolved Contradictions

## Active Questions

No active questions remain.

The Critic found sufficient evidence to form a view.

---

## Unresolved Contradictions

No unresolved contradictions.

All detected contradictions were either resolved or flagged for human review.

---

# 7. Appendix

## Methodology

Full 7-step pipeline explanation.

---

## Key Design Principles

- No fake probabilities
- Explicit uncertainty
- Evidence provenance
- Deterministic analysis
- Contradiction-first reasoning

---

## Limitations

- Public data only
- Live RSS feeds
- Single GitHub snapshot
- Closing prices only

---

## Disclaimer

Educational/research purposes only.

---

# Three Assets, Three Behaviors

| Asset | Dimensions | Iterations | Halt Reason | Bias | Uncertainty | Key Behavior |
|---|---|---|---|---|---|---|
| AAPL | 3 of 3 | 3 (circuit) | max_iterations | BEARISH | 17% Low | Contradictions persisted; full depth needed |
| Bitcoin | 3 of 3 | 3 (circuit) | max_iterations | BEARISH | 17% Low | High drawdown (53.1%) dominated thesis |
| Rust | 2 of 3 | 1 | coherent_view | BULLISH | 35% Moderate | Strong alignment; halted immediately |

---

The number of iterations is information.

AAPL and Bitcoin needed all 3 tiers because evidence was contradictory.

Rust halted at iteration 1 because Business and Technical agreed.

The loop is genuinely adaptive.

---
# Architecture

```text
                         User Request
                              │
                              ▼
                   Research Controller
                      (Loop Engine)
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
      Quant Agent       Technical Agent     Business Agent
   (Tiered: 3mo→6mo→1y)   (GitHub API)        (RSS + Ollama)
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
                    Evidence Register
                    (core/evidence.py)
                              │
                              ▼
                       Critic Agent
                  (6-Phase Rule-Based)
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    More Research Needed                 Hypothesis Engine
    (contradictions persist)          (Directional Bias +
                                          Uncertainty)
                                              │
                                              ▼
                                        Risk Agent
                                              │
                                              ▼
                                     Report Generator
                                    (Jinja2 → Markdown / PDF)
                                              │
                                              ▼
                                       Investment Memo
```

---

# Non-Negotiable Principles

AIRS follows strict design rules.

| Principle | Implementation |
|---|---|
| Critic Agent | 100% rule-based. No LLM decides when to halt. |
| Evidence Register | Single source of truth for all evidence. |
| Financial Analysis | Deterministic. No LLM computes statistics. |
| Hypothesis Generation | Evidence-weighted, never normalized to 100%. |
| Uncertainty | Independent from directional conviction. |

---

# Agent Overview

| Agent | Purpose | Uses LLM? | Iterates? |
|---|---|---|---|
| 📊 Quant Agent | Returns, volatility, momentum, RSI, MACD, drawdown, risk score, trend, beta, correlation | ❌ No | ✅ Yes (3 tiers) |
| 🖥️ Technical Agent | GitHub commits, contributors, repository health | ❌ No | ❌ No (bootstrap) |
| 📰 Business Agent | RSS news, signal extraction, catalysts, risks | ✅ Yes (Ollama) | ❌ No (bootstrap) |
| ⚠️ Risk Agent | Downside analysis, contradiction detection | ❌ No | ❌ No |
| 🔍 Critic Agent | 6-phase research director, dashboard-driven halt | ❌ No (Rule-based) | ✅ Evaluates every iteration |

---

# Project Structure

```text
AIRS/
│
├── agents/
│   ├── quant.py              # Tiered numerical analysis (pandas/NumPy)
│   ├── technical.py          # GitHub ecosystem health
│   ├── business.py           # RSS news + Ollama summarization
│   ├── risk.py               # Rule-based downside analysis
│   └── critic.py             # 6-phase research director
│
├── controller/
│   └── loop.py               # Evidence-driven loop controller (max 3 iterations)
│
├── core/
│   └── evidence.py           # Evidence Register (single source of truth)
│
├── data/
│   ├── db.py                 # SQLite database layer
│   └── fetcher.py            # yfinance wrapper with retry logic
│
├── reports/
│   ├── hypothesis.py          # Directional Bias + Uncertainty engine
│   ├── generator.py           # Jinja2 Markdown/PDF report generator
│   └── templates/
│       └── report.md.j2       # Seven-section investment memo template
│
├── utils/
│   └── ollama_client.py      # Ollama client with retry logic
│
├── docs/
│   ├── research/
│   │   ├── DESIGN_PHILOSOPHY.md
│   │   ├── EVALUATION.md
│   │   ├── CASE_STUDIES.md
│   │   └── LIMITATIONS.md
│   │
│   ├── architecture/
│   │   ├── ARCHITECTURE.md
│   │   └── DECISIONS.md
│   │
│   ├── development/
│   │   ├── ROADMAP.md
│   │   ├── CHANGELOG.md
│   │   ├── CURRENT_TASK.md
│   │   ├── LEARNING.md
│   │   └── PROJECT_NOTES.md
│   │
│   └── SETUP.md
│
├── tests/
│
├── main.py                   # CLI entry point
├── requirements.txt
└── README.md
```

---

# Quick Start

## 1. Clone & Setup

```bash
git clone https://github.com/deadpool-kha/AIRS.git

cd AIRS
```

---

Create virtual environment:

```bash
python -m venv venv
```

---

## Windows

```bash
venv\Scripts\activate
```

---

## macOS / Linux

```bash
source venv/bin/activate
```

---

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 2. Install Ollama

Download Ollama:

```
https://ollama.com
```

Pull the model:

```bash
ollama pull qwen2.5:7b
```

Start Ollama:

```bash
ollama serve
```

Keep Ollama running in a separate terminal.

---

# 3. Run AIRS

## Full research loop — public stock

```bash
python main.py --entity AAPL --ticker AAPL --hypotheses
```

---

## With GitHub repository

```bash
python main.py --entity AAPL --ticker AAPL --repo apple/swift --hypotheses
```

---

## With PDF export

```bash
python main.py --entity AAPL --ticker AAPL --repo apple/swift --hypotheses --pdf
```

---

## Crypto with repository

```bash
python main.py --entity bitcoin --ticker BTC-USD --repo bitcoin/bitcoin --hypotheses
```

---

## Open-source project (no market data)

```bash
python main.py --entity rust-lang --repo rust-lang/rust --hypotheses
```

---

## Single-shot modes

Quant only:

```bash
python main.py --entity AAPL --quant-only
```

Business only:

```bash
python main.py --entity NVIDIA --business-only
```

Technical only:

```bash
python main.py --repo bitcoin/bitcoin --technical-only
```

---
# CLI Reference

| Argument | Description |
|---|---|
| `--entity` | Company or asset name (e.g., AAPL, Bitcoin, rust-lang) |
| `--ticker` | Stock or crypto ticker for quantitative analysis |
| `--repo` | GitHub repository in `owner/repo` format |
| `--hypotheses` | Run the full evidence-driven research loop |
| `--pdf` | Also generate PDF report (requires WeasyPrint; graceful fallback if unavailable) |
| `--quant-only` | Run only the Quant Agent |
| `--technical-only` | Run only the Technical Agent |
| `--business-only` | Run only the Business Agent |
| `--show-sources` | Display evidence provenance and source tracking |
| `--period` | Quant analysis period: `1mo`, `3mo`, `6mo`, `1y` |

---

## Deprecated Flags

The following standalone flags are deprecated:

```
--risk-only
--critic
```

Risk and Critic now run automatically inside:

```bash
--hypotheses
```

---

# Documentation

| Document | Location | What It Covers |
|---|---|---|
| Design Philosophy | `docs/research/DESIGN_PHILOSOPHY.md` | Why AIRS exists, core principles, what it is/isn't |
| Evaluation Framework | `docs/research/EVALUATION.md` | How research quality is measured, manual test cases |
| Case Studies | `docs/research/CASE_STUDIES.md` | Real sessions: AAPL, Bitcoin, Rust, Oracle |
| Limitations | `docs/research/LIMITATIONS.md` | Known boundaries and constraints |
| Architecture | `docs/architecture/ARCHITECTURE.md` | Full 7-layer system architecture |
| Decision Log | `docs/architecture/DECISIONS.md` | Why Jinja2, why SQLite, why rule-based Critic |
| Roadmap | `docs/development/ROADMAP.md` | Phase-based development plan |
| Changelog | `docs/development/CHANGELOG.md` | Version history |
| Current Task | `docs/development/CURRENT_TASK.md` | Active development tracker |
| Learning Log | `docs/development/LEARNING.md` | Knowledge capture from implementation |
| Project Notes | `docs/development/PROJECT_NOTES.md` | Long-term project memory |
| Setup Guide | `docs/SETUP.md` | Installation, dependencies, troubleshooting |

---

# Current Status: v0.3.7

| Component | Status |
|---|---|
| Data Layer (SQLite + yfinance) | ✅ Complete |
| Quant Agent (Tiered: 3mo / 6mo / 1y) | ✅ Complete |
| Technical Agent (GitHub REST API) | ✅ Complete |
| Business Agent (RSS + Ollama) | ✅ Complete |
| Risk Agent (Rule-based) | ✅ Complete |
| Critic Agent v2 (6-phase analyst) | ✅ Complete |
| Evidence Register (Provenance tracking) | ✅ Complete |
| Hypothesis Engine v3 (Bias + Uncertainty) | ✅ Complete |
| Loop Controller v2 (Adaptive halt) | ✅ Complete |
| Report Generator (Jinja2 Markdown + PDF) | ✅ Complete |
| Audit Trail & Backtesting | 🚧 Phase 9 (Active) |
| Streamlit Web Interface | 📅 Planned |

---

# Roadmap at a Glance

| Phase | Feature | Status |
|---|---|---|
| 1 | Data Foundation | ✅ |
| 2 | Quant Agent | ✅ |
| 3 | Technical Agent | ✅ |
| 4 | Business Agent | ✅ |
| 5 | Risk Agent | ✅ |
| 6 | Critic Agent | ✅ |
| 7 | Loop Controller | ✅ |
| 8 | Report Generator | ✅ |
| 9 | Audit Trail & Backtesting | 🚧 Active |
| 10 | Streamlit Interface | 📅 Planned |

---

# Design Principles

| Principle | Implementation |
|---|---|
| Evidence Before Conclusions | Every claim traces back to the Evidence Register |
| Explicit Uncertainty | Separate from directional bias; computed from scarcity, conflict, coverage |
| Contradiction-First Thinking | 12 deterministic rules surface conflicts instead of averaging them away |
| Deterministic Analysis | No LLM computes statistics, indicators, or halt decisions |
| Research Is Iterative | 3-tier quant with dashboard-driven early stopping |
| Local-First | Ollama + SQLite + yfinance. Zero paid APIs |

---

# What This Project Demonstrates

AIRS was built as a portfolio project showcasing practical AI engineering:

## Multi-Agent Systems

5 specialized agents with distinct responsibilities:

- Quant Agent
- Technical Agent
- Business Agent
- Risk Agent
- Critic Agent

---

## Loop Engineering

Self-improving research with deterministic quality gates.

The system demonstrates:

- Iterative evidence collection
- Research feedback loops
- Adaptive stopping conditions
- Quality-controlled AI workflows

---

## Evidence-Based Workflows

AIRS focuses on:

- Provenance tracking
- Auditability
- Transparency
- Explainable conclusions

---

## Quantitative Finance

Real analysis using:

- pandas
- NumPy
- yfinance

Not LLM-generated financial calculations.

---

## Local LLM Integration

Ollama is used for:

- Summarization
- Signal extraction
- Qualitative analysis

Never for:

- Statistics
- Indicators
- Research decisions

---

## Software Architecture

Clean separation between:

- Data
- Agents
- Controller
- Evidence
- Reports

---
# Current Limitations

| Area | Limitation |
|---|---|
| Business Agent | Uses live RSS only. Historical news archives are not available. |
| Technical Agent | Evaluates a single GitHub snapshot per session. |
| Iteration Updates | Only the Quant Agent currently receives updated inputs between iterations. |
| Hypothesis Engine | Strength thresholds are heuristic and not yet backtested. |
| Risk Agent | Still reads from a legacy bridge. Direct Evidence Register integration is planned. |
| PDF Export | Requires GTK+ libraries on Windows because of the WeasyPrint dependency. |

See:

```
docs/research/LIMITATIONS.md
```

for full details.

---

# Future Direction

The long-term opportunity is building an:

> **AI-native research infrastructure layer**

supporting:

- Venture capital due diligence
- Hedge fund research workflows
- Market intelligence
- Competitive analysis
- Startup evaluation
- Open-source ecosystem analysis


The common problem:

> Turning massive amounts of information into structured, trustworthy decisions.

---

# Why AIRS Exists

Most AI research systems optimize for:

```
Question → Answer
```

AIRS optimizes for:

```
Evidence → Reasoning → Audit → Decision
```

The goal is not simply producing answers.

The goal is producing answers that can explain:

- Where the information came from
- Why a conclusion was reached
- What evidence supports it
- What remains uncertain

---

# Contributing

Contributions are welcome.

Areas that can improve AIRS:

- Additional evidence sources
- Historical datasets
- Better evaluation frameworks
- Improved backtesting
- New report formats
- Research quality metrics


Before contributing:

1. Read the architecture documentation.
2. Understand the Evidence Register design.
3. Preserve deterministic financial logic.
4. Keep provenance tracking intact.

---

# Development Philosophy

AIRS follows these rules:

## Add More Evidence Before Adding More Agents

The system prioritizes:

- Better data
- Better auditing
- Better validation

over simply increasing the number of agents.

---

## Explainability Over Prediction

AIRS does not attempt to predict markets.

It focuses on:

- Structured research
- Evidence quality
- Transparent reasoning

---

## Local First

The system runs locally using:

- SQLite
- Ollama
- yfinance

No paid APIs are required.

---

# Disclaimer

AIRS is an educational and research project.

It does **not** provide financial advice and should not be used as the sole basis for investment decisions.

All outputs are generated from:

- Publicly available data
- Deterministic calculations
- Structured reasoning workflows
- Local language models used only for qualitative tasks


Independent research and professional judgment are essential before making financial decisions.

---

<div align="center">

# AIRS v0.3.7

## Evidence-Driven Investment Research Infrastructure

**Research should be explainable before it is persuasive.**

</div>