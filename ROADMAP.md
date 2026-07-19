# ROADMAP.md

# Project: Autonomous Investment Research System (AIRS)

## Timeline

Target completion:

20 days

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

Working system > beautiful interface > advanced features

---

# Phase 0: Setup

## Day 1

Objectives:

Create project foundation.

Tasks:

* Create GitHub repository
* Create Python virtual environment
* Setup folder structure
* Setup README
* Create MEMORY.md
* Create ROADMAP.md
* Create DECISIONS.md

Repository:

```
AIRS/

├── README.md
├── MEMORY.md
├── ROADMAP.md
├── DECISIONS.md

├── backend/

├── agents/

├── data/

├── database/

├── models/

├── frontend/

└── tests/
```

Deliverable:

Empty but organized project.

---

# Phase 1: Data Foundation

## Days 2-4

Goal:

Build the data layer.

---

## Market Data Module

Collect:

* historical prices
* volume
* market information

Possible sources:

* Yahoo Finance
* CoinGecko

Create:

```
data/market_data.py
```

Output:

Structured data.

Example:

```
Asset:
ETH

Price:
xxxx

30 day return:
x%

Volatility:
x%

Volume:
x%
```

---

## Database

Create SQLite database.

Tables:

```
entities

market_data

news

github_activity

research_results
```

---

Deliverable:

The system can collect and store market data.

---

# Phase 2: Quant Agent

## Days 5-6

Goal:

Create first analytical agent.

Important:

This is NOT an LLM agent.

It is a Python analysis module.

---

Capabilities:

Calculate:

* returns
* volatility
* moving averages
* momentum
* drawdown
* risk score

Example output:

```
Quant Analysis:

Trend:
Positive

Momentum:
Strong

Risk:
Medium

Confidence:
75%
```

---

Deliverable:

Given an asset:

The system produces quantitative analysis.

---

# Phase 3: Technical Agent

## Days 7-9

Goal:

Analyze engineering activity.

---

Data source:

GitHub API.

Collect:

* contributors
* commits
* releases
* issues

---

Metrics:

Developer growth

Contribution frequency

Project activity

Maintenance health

Example output:

```
Technical Health:

Developer Activity:
Increasing

Contributor Growth:
+35%

Project Status:
Healthy
```

---

Deliverable:

The system can evaluate technical ecosystem health.

---

# Phase 4: Business and News Agent

## Days 10-12

Goal:

Understand external events.

---

Sources:

* RSS feeds
* public announcements
* websites

Collect:

* partnerships
* funding
* launches
* major events

---

Use LLM only here.

Pipeline:

News

↓

Retrieve relevant information

↓

Local LLM summary

Output:

```
Business Analysis:

Positive catalysts:
- New partnership
- Product release

Risks:
- Competition
```

---

Deliverable:

System understands qualitative information.

---

# Phase 5: Risk Agent

## Days 13-14

Goal:

Build downside analysis.

---

Analyze:

* negative news
* competition
* volatility
* concentration risk
* uncertainty

---

Output:

```
Risk Assessment:

High risks:

1. Competition
2. Valuation
3. Regulatory uncertainty

Overall Risk:
Medium
```

---

Deliverable:

System does not only produce bullish reports.

---

# Phase 6: Loop Engine

## Days 15-16

Goal:

Implement controlled agent workflow.

---

The loop:

```
Receive research request

↓

Create research plan

↓

Collect evidence

↓

Run agents

↓

Critic evaluates quality

↓

Missing information?

YES:
Continue research

NO:
Generate report
```

---

Components:

```
controller.py

planner.py

critic.py

memory.py
```

---

Deliverable:

The system can decide whether research is complete.

---

# Phase 7: Investment Committee Writer

## Days 17-18

Goal:

Generate final research memo.

---

Input:

All agent outputs.

Example:

```
Quant:
Positive momentum

Technical:
Developer activity increasing

Business:
New partnership

Risk:
Competition increasing
```

---

LLM generates:

```
Investment Committee Report

Overview:

Bull Case:

Bear Case:

Key Risks:

Open Questions:

Conclusion:
```

---

Deliverable:

Professional research report.

---

# Phase 8: Interface and Presentation

## Days 19-20

Goal:

Make project presentable.

---

Build:

Simple Streamlit interface.

Features:

* select entity
* run analysis
* display report
* show evidence

---

Create:

README improvements

Screenshots

Architecture diagram

Demo video

---

Final deliverable:

A working AI investment research system.

---

# Minimum Viable Version

If time becomes limited:

Must have:

YES:

* Quant Agent
* Technical Agent
* Loop Controller
* LLM Report Generator

Optional:

* UI
* Business Agent
* Advanced ML

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

---

# Success Criteria

The project is successful if:

1. A stranger can understand it from GitHub.
2. A user can run an analysis.
3. The system produces a structured report.
4. Architecture demonstrates modern AI engineering.
5. The developer can explain every design decision.
