# AIRS — Autonomous Investment Research System
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)
![AI](https://img.shields.io/badge/Architecture-Multi--Agent_AI-purple)


> An AI-powered multi-agent investment research platform that automates the workflow of a professional investment research team.

Built with **Python**, **SQLite**, and **local LLMs (Ollama)**.

**Goal:** Produce structured, evidence-based investment research—not price predictions.

---

## ✨ Features

- 📊 Multi-agent investment research workflow
- 🤖 Local LLM integration (Ollama)
- 📈 Quantitative financial analysis
- 📰 News analysis and signal extraction
- 🖥️ GitHub ecosystem analysis
- ⚠️ Automated downside risk assessment
- 🔍 Research quality validation with Critic Agent
- 🔁 Iterative research loop (coming soon)
- ⚖️ Evidence-based Bull/Bear/Base hypotheses
- 📚 Source tracking and auditable confidence scores
- 💰 Zero API cost development

---

# What AIRS Does

Run a single command:

```bash
python main.py --entity AAPL --repo apple/swift --ticker AAPL --hypotheses
```

AIRS performs an investment committee workflow automatically.

| Agent | Purpose | Uses LLM? | Status |
|-------|---------|-----------|--------|
| 📊 **Quant Agent** | Returns, volatility, momentum, drawdown, risk score, trend | No | ✅ Ready |
| 🖥️ **Technical Agent** | GitHub commits, contributors, repository health | No | ✅ Ready |
| 📰 **Business Agent** | News analysis, signals, catalysts, risks | Yes (Ollama) | ✅ Ready |
| ⚠️ **Risk Agent** | Downside analysis, contradiction detection | No | ✅ Ready |
| 🔍 **Critic Agent** | Research quality, gap detection, iteration trigger | Yes (Ollama) | ✅ Ready |

After all agents finish, AIRS generates:

- Evidence-backed investment analysis
- Confidence scores
- Source tracking
- Cross-agent validation
- Bull / Bear / Base investment hypotheses

---

# Example Output

```text
==================================================
QUANT ANALYSIS: AAPL
==================================================
Trend: strong_uptrend
Current Price: $326.59
Volatility (annual): 28.28%
Risk Score: 0.3138
Max Drawdown: 12.71%
Weekly Return: 3.73%
Monthly Return: 9.59%
Confidence: 0.90

==================================================
TECHNICAL ANALYSIS: apple/swift
==================================================
Total Commits: 100
Commit Frequency: 233.33/week
Contributors: 30
Open Issues: 9130
Days Since Commit: 0
Health Score: 0.70
Confidence: 0.85

==================================================
BUSINESS ANALYSIS: AAPL
==================================================
Signals Found: 2
Catalysts: 1
Risks: 1
Confidence: 0.7033

==================================================
RISK ANALYSIS
==================================================
Overall Risk: HIGH
Risks Found: 1
Warnings: 1

==================================================
CRITIC EVALUATION
==================================================
Overall Quality: PARTIAL
Quality Score: 0.875
Should Iterate: True

==================================================
INVESTMENT HYPOTHESES
==================================================

Bull Case (38%)
+ Strong price momentum
+ Strong monthly returns
+ Active developer ecosystem

Bear Case (25%)
+ High overall risk
+ Consumer privacy concerns

Base Case (38%)
+ Moderate risk
+ Healthy ecosystem
+ Stable volatility
```

---

# Architecture

```text
                    User Request
                         │
                         ▼
          Research Controller (Loop Engine)
                         │
                         ▼
                  Research Agents
        ┌─────────┬─────────┬─────────┐
        ▼         ▼         ▼         ▼
     Quant    Technical  Business   Risk
        └─────────┬─────────┬─────────┘
                  ▼
            Critic Agent
                  │
      Iterate? (Maximum 3 loops)
                  │
                  ▼
      Hypothesis Competition Engine
                  │
                  ▼
      Investment Research Report
```

---

# Technology Stack

| Layer | Technology |
|--------|------------|
| Language | Python 3.11+ |
| Database | SQLite |
| Market Data | Yahoo Finance (yfinance) |
| GitHub Data | GitHub REST API |
| News Data | RSS Feeds |
| LLM Runtime | Ollama |
| LLM Model | Qwen 2.5 7B |
| Future Backend | FastAPI |
| Future Frontend | Streamlit |

---

# Project Structure

```text
AIRS/
│
├── agents/
│   ├── quant.py
│   ├── technical.py
│   ├── business.py
│   ├── risk.py
│   └── critic.py
│
├── controller/
│   └── loop.py
│
├── data/
│   ├── db.py
│   └── fetcher.py
│
├── reports/
│   └── hypothesis.py
│
├── utils/
│   └── ollama_client.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
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
├── main.py
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

Download Ollama:

https://ollama.com

Pull the model:

```bash
ollama pull qwen2.5:7b
```

Start the Ollama server:

```bash
ollama serve
```

Keep the Ollama server running in a separate terminal.

---

# 💻 Usage

## Quant Analysis

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

## Risk Analysis

```bash
python main.py --entity AAPL --repo apple/swift --hypotheses
```

---

## Full Research Pipeline

```bash
python main.py --entity AAPL --repo apple/swift --ticker AAPL --hypotheses
```

---

## Show Source Tracking

```bash
python main.py --entity AAPL --quant-only --show-sources
```

---

# ⚙️ Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--entity` | Company or asset name |
| `--ticker` | Stock ticker symbol |
| `--repo` | GitHub repository |
| `--quant-only` | Run only Quant Agent |
| `--technical-only` | Run only Technical Agent |
| `--business-only` | Run only Business Agent |
| `--risk-only` | Run only Risk Agent |
| `--critic` | Run only Critic Agent |
| `--hypotheses` | Generate Bull/Bear/Base hypotheses |
| `--show-sources` | Display evidence sources |

---

# 📊 Current Development Status

**Current Version:** `v0.3.5`

## ✅ Completed

- Data Foundation
- SQLite database
- Market data fetcher
- Quant Agent v2
- Technical Agent
- Business Agent
- Risk Agent
- Critic Agent
- Hypothesis Competition Engine

---

## 🚧 In Progress

- Loop Controller
- Report Generator
- Research orchestration
- Graceful degradation
- Better CLI experience

---

# 🎯 Key Features

### 🏠 Local-First AI

Everything runs locally.

- No OpenAI API required
- No paid APIs
- Low operating cost
- Works offline (except market/news retrieval)

---

### 📊 Deterministic Financial Analysis

Financial calculations never rely on an LLM.

Examples include:

- Returns
- Volatility
- Drawdown
- Risk scores
- Momentum
- Trend detection

---

### 🤖 AI Where It Matters

LLMs are used only for tasks that benefit from reasoning.

Examples:

- News summarization
- Signal extraction
- Research critique
- Report generation
- Investment reasoning

---

### 🔁 Loop Engineering

Instead of generating one answer and stopping:

Research → Critique → Improve → Repeat

The Critic Agent decides whether another research iteration is needed.

Maximum iterations: **3**

---

### ⚖️ Hypothesis Competition

Instead of producing a single recommendation, AIRS generates competing hypotheses.

- 🟢 Bull Case
- 🔴 Bear Case
- ⚪ Base Case

Each hypothesis must cite evidence from the research pipeline.

---

### 📚 Auditable Confidence

Every confidence score is traceable.

No arbitrary AI confidence values.

Confidence is calculated from:

- Data quality
- Metric completeness
- Supporting evidence
- Cross-agent validation

---

### 🔍 Cross-Agent Validation

The Critic Agent checks whether agents contradict each other.

Example:

- Quant says "Strong Uptrend"
- Business says "Extremely Negative News"

The Critic flags the inconsistency and requests another iteration.

---

# 📖 Documentation

| File | Description |
|------|-------------|
| `ARCHITECTURE.md` | System architecture |
| `CHANGELOG.md` | Version history |
| `CURRENT_TASK.md` | Current development work |
| `DECISIONS.md` | Engineering decision log |
| `LEARNING.md` | Lessons learned |
| `MEMORY.md` | AI assistant context |
| `ROADMAP.md` | Project roadmap |
| `SETUP.md` | Installation guide |
| `SPEC.md` | Product specification |

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
| Hypothesis Engine | ✅ Complete |
| Loop Controller | 🚧 In Progress |
| Report Generator | 🚧 In Progress |
| Web Interface | 📅 Planned |
| API | 📅 Planned |

---

# 🗺️ Roadmap

## ✅ Phase 1 — Data Foundation

- SQLite database
- Market data fetcher
- Data persistence
- Retry logic
- Source tracking

---

## ✅ Phase 2 — Quant Agent

- Returns
- Volatility
- Momentum
- Trend detection
- Drawdown
- Risk score
- Auditable confidence

---

## ✅ Phase 3 — Technical Agent

- GitHub REST API integration
- Commit activity
- Contributor analysis
- Repository health score

---

## ✅ Phase 4 — Business Agent

- RSS news ingestion
- Ollama integration
- News summarization
- Signal extraction
- Catalyst detection

---

## ✅ Phase 5 — Risk Agent

- Downside analysis
- Cross-agent contradiction detection
- Blind-spot identification
- Risk severity scoring

---

## ✅ Phase 6 — Critic Agent

- Research quality evaluation
- Gap detection
- Cross-agent validation
- Iteration trigger
- Optional LLM suggestions

---

## 🚧 Phase 7 — Loop Controller

- Research planning
- Automatic iteration
- Graceful degradation
- State persistence
- Dynamic agent orchestration

---

## 📅 Phase 8 — Report Generator

- Professional investment memo
- Executive summary
- Evidence register
- Research citations
- Final recommendation structure

---

## 📅 Future

- FastAPI backend
- Streamlit dashboard
- Portfolio analysis
- Multi-company comparison
- Earnings transcript analysis
- SEC filing analysis
- Crypto research support
- Docker deployment
- CI/CD pipeline

---

# 🏗️ Design Principles

- **Evidence over opinions**
- **Deterministic calculations whenever possible**
- **Use LLMs only where reasoning adds value**
- **Every conclusion should be traceable**
- **Research should improve through iteration**
- **Keep development costs near zero**

---

# 🎓 What This Project Demonstrates

AIRS was built as a portfolio project demonstrating knowledge of:

- Multi-Agent AI Systems
- Agent Orchestration
- Loop Engineering
- Financial Research Workflows
- Quantitative Analysis
- Local LLM Integration
- Python Software Engineering
- SQLite Database Design
- GitHub API Integration
- RSS Data Processing
- Software Architecture
- AI Evaluation Systems

---

# 🔬 Research Philosophy

Unlike many AI investment tools that generate a single opinion, AIRS follows an investment committee approach.

Each agent specializes in one domain:

- Quantitative analysis
- Technical ecosystem analysis
- Business and news analysis
- Risk assessment
- Research quality evaluation

Rather than trusting a single model, AIRS combines independent analyses, validates them, and produces competing hypotheses supported by evidence.

---

# ⚠️ Current Limitations

- Loop Controller is still under development.
- Report Generator is not yet complete.
- Business Agent requires Ollama to be running.
- Market data depends on Yahoo Finance availability.
- GitHub API is subject to unauthenticated rate limits (60 requests/hour).

---

# 🤝 Contributing

Contributions, bug reports, feature requests, and suggestions are welcome.

If you'd like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

---

# 📄 License

This project is licensed under the **MIT License**.

---

# ⚠️ Disclaimer

**AIRS is an educational and research project.**

It is **not** financial advice and should not be used as the sole basis for investment decisions.

The system organizes publicly available information into structured research reports, but all investment decisions require independent research and professional judgment.

---

## ⭐ If you found this project interesting, consider giving it a star!

It helps others discover the project and motivates continued development.

---
