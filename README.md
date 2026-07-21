# AIRS — Autonomous Investment Research System

An AI-powered investment research platform that automates the workflow of a professional investment research team.

Built with **Python**, **SQLite**, and **local LLMs (Ollama)**.  
Designed for **zero API costs** during development.

---

# Example Output

```text
QUANT ANALYSIS: AAPL

Trend: strong_uptrend
Current Price: $326.59
Volatility (annual): 25.43%
Risk Score: 0.3124
Max Drawdown: 7.36%
Weekly Return: 3.71%
Monthly Return: 8.23%
Confidence: 0.85
```

---

# Architecture

```text
User Request
      |
      v
Research Controller
      |
      v
    Agents
      |
      v
   Critic Agent
      |
      v
Report Generator


        |
        v

Data Layer (SQLite)

        |
        v

External APIs
(Yahoo Finance, GitHub, News)
```

---

# Agents

| Agent | Purpose |
|-------|---------|
| 📊 **Quant Agent** | Numerical analysis including returns, volatility, momentum, risk scoring, and trends |
| 🖥️ **Technical Agent** | GitHub ecosystem health analysis using commits, contributors, and issues |
| 📰 **Business Agent** | Business signals and news analysis |
| ⚠️ **Risk Agent** | Downside analysis and weakness identification |
| 🔍 **Critic Agent** | Research quality evaluation and loop engineering |

---

# Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| Database | SQLite |
| Market Data | Yahoo Finance (`yfinance`) |
| LLM Runtime | Ollama (local, free) |
| Web Framework | FastAPI *(future)* |
| Frontend | Streamlit *(future)* |

---

# Development Philosophy

### 🏠 Local-First
No paid APIs required during development.

### 🧩 Modular
Each research agent is independent and can evolve separately.

### 🎯 Deterministic
Financial calculations are performed using pure Python without LLM dependency.

### 🔁 Iterative
Loop engineering improves research quality through repeated evaluation.

---

# Project Structure

```text
AIRS/
│
├── main.py                  # CLI entry point
│
├── data/                    # Database and data fetching
│   ├── db.py
│   └── fetcher.py
│
├── agents/                  # Analysis agents
│   ├── quant.py
│   ├── technical.py
│   ├── business.py
│   ├── risk.py
│   └── critic.py
│
├── controller/              # Research orchestration
│   └── loop.py
│
├── reports/                 # Report generation
│   └── generator.py
│
├── utils/                   # Utility functions
│   └── ollama_client.py
│
└── tests/                   # Unit tests
```

---

# Documentation

| File | Purpose |
|------|---------|
| `MEMORY.md` | Project context and architecture |
| `ROADMAP.md` | Development phases and timeline |
| `ARCHITECTURE.md` | System architecture |
| `SPEC.md` | Product specification |
| `SETUP.md` | Developer setup guide |
| `CURRENT_TASK.md` | Development status |
| `DECISIONS.md` | Engineering decision log |
| `LEARNING.md` | Knowledge capture |
| `CHANGELOG.md` | Version history |

---

# Current Status

## Working Features

- ✅ Fetch market data from Yahoo Finance (free, no API key)
- ✅ Store market data in SQLite database
- ✅ Quant Agent:
  - Returns calculation
  - Volatility analysis
  - Momentum detection
  - Maximum drawdown calculation
  - Risk scoring
  - Trend identification
- ✅ CLI interface:

```bash
python main.py --entity AAPL --quant-only
```

---

# Coming Soon

- ⏳ Technical Agent (GitHub ecosystem analysis)
- ⏳ Business Agent (news analysis)
- ⏳ Risk Agent (downside analysis)
- ⏳ Critic Agent (research quality evaluation)
- ⏳ Loop Controller (iterative improvement system)
- ⏳ Report Generator (investment research memo)

---

# Quick Start

## Clone Repository

```bash
git clone https://github.com/deadpool-kha/AIRS.git

cd AIRS
```

## Install Dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Run Analysis

```bash
python main.py --entity AAPL --quant-only
```

---

# License

MIT