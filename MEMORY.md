# MEMORY.md

# Project: Autonomous Investment Research System (AIRS)

## Role of This Document

This file provides the complete context of the project for AI assistants and developers.

When assisting with this project:

- Understand the architecture before suggesting changes.
- Do not redesign the system unless explicitly requested.
- Prefer simple, reliable engineering solutions.
- Explain tradeoffs behind technical decisions.
- Prioritize completing the MVP.

---

# Project Goal

Build an AI-powered investment research system that automates the workflow of an investment research team.

The system should analyze:

1. Public companies
   - Example: NVIDIA, Tesla
2. Crypto protocols/assets
   - Example: Ethereum, Solana, Stacks
3. AI companies/startups
   - Using publicly available information

The goal is **NOT** to predict stock or crypto prices.

The goal is to create structured, evidence-based research reports.

---

# Why This Project Exists

This project is being built as:

1. A portfolio project for AI/software engineering roles.
2. A demonstration of modern AI engineering skills.
3. A practical exploration of investment research automation.

The project combines:

- AI agents
- Loop engineering (Andrew Ng's concept)
- Quantitative analysis
- Data engineering
- Financial research workflows

---

# Core Product Vision

User provides:

> "Analyze [entity]"

Example:

> "Analyze NVIDIA"

The system performs an investment committee workflow:

1. Collect evidence
2. Analyze data
3. Evaluate risks
4. Critique the research
5. Iterate if needed
6. Generate a final research memo

---

# Important Engineering Principle

Do **NOT** use LLMs for everything.

Use traditional programming for:

- Calculations
- Metrics
- Data processing
- Database operations
- Deterministic analysis

Use LLMs for:

- Planning
- Reasoning
- Critique
- Summarization
- Final report generation

The LLM is a reasoning layer, not the entire system.

---

# High-Level Architecture

```text
                     User
                      |
                      |
              Research Request
                      |
                      |
          Research Controller
            (Loop Engine)
                      |
    -----------------------------------
    |          |          |           |
    v          v          v           v

 Quant     Technical   Business     Risk
 Agent      Agent       Agent      Agent

    |          |          |           |
    -----------------------------------
                      |
                      v
               Critic Agent
                      |
          ----------------------
          |                    |
    More Research        Final Report
                      |
                      v
         Investment Committee Memo
```

---

# Core Components

## 1. Data Layer

Responsible for collecting external information.

### Market Data

Examples:

- Yahoo Finance (`yfinance`)
- CoinGecko

Data collected:

- Price
- Volume
- Returns
- Volatility

### Technical Data

Source:

- GitHub API

Data collected:

- Commits
- Contributors
- Releases
- Issues

### Business Data

Sources:

- RSS feeds
- Company websites
- Public announcements

Data collected:

- Partnerships
- Funding
- Product launches
- Important events

---

# 2. Database Layer

Initial database:

- SQLite

Future possibility:

- PostgreSQL

Stores:

- Entities
- Market data
- GitHub activity
- News
- Research results
- Agent states
- Loop iteration history

---

# 3. Agents

Agents are specialized modules.

They are **NOT** separate ChatGPT conversations.

---

## Quant Agent

### Purpose

Analyze numerical information.

### Responsibilities

- Price trends
- Returns
- Volatility
- Momentum
- Drawdown
- Risk metrics

### Implementation

Python

Libraries:

- pandas
- numpy
- Statistics libraries

No LLM required.

---

## Technical Agent

### Purpose

Analyze technical ecosystem health.

### Data

- GitHub activity

### Metrics

- Contributor growth
- Commit frequency
- Release activity
- Project maintenance

### Implementation

Python

May use an LLM for summary only.

---

## Business Agent

### Purpose

Analyze qualitative business information.

### Inputs

- News
- Announcements
- Public information

Uses a local LLM for summarization and extraction.

---

## Risk Agent

### Purpose

Find weaknesses and negative signals.

### Examples

- Competition
- Regulatory concerns
- Declining activity
- High-risk factors

Uses:

- Rules
- Data analysis
- LLM reasoning when useful

---

## Critic Agent

### Purpose

Evaluate research quality.

Before generating the final report, it checks:

- Is enough evidence collected?
- Are claims supported?
- Are risks considered?
- Is information missing?

If research is incomplete:

The loop continues with targeted iteration.

---

# Loop Engineering Design

The system uses a controlled research loop inspired by Andrew Ng's loop engineering.

## Research Loop

```text
Receive Goal
      ↓
Create Research Plan
      ↓
Collect Evidence
      ↓
Run Analysis Agents
      ↓
Evaluate Research Quality
   (Critic Agent)
      ↓
Missing Information?
      ↓
  YES         NO
   |           |
Continue     Generate
Research      Final Report
(Targeted
Iteration)
```

The loop controller decides workflow progression.

Maximum iterations: **3**

After three iterations, generate a best-effort report with confidence flags.

The LLM does **NOT** control everything.

---

# LLM Architecture

Local-first approach.

No paid APIs during development.

### Runtime

- Ollama

### Possible Models

- Qwen 2.5 7B
- Llama 3.1 8B
- Mistral 7B

### LLM Responsibilities

- Planning
- Reasoning
- Critique
- Writing reports

---

# Hardware Environment

### Development Machine

**GPU**

- NVIDIA GTX 1060 6GB

**RAM**

- 16 GB

**Operating System**

- Windows 10

### Constraint

Development cost target:

**$0**

---

# Technology Stack

## Backend

- Python
- FastAPI (future)

## Database

- SQLite

## AI Runtime

- Ollama

## Vector Search

- FAISS or ChromaDB (future)

## Frontend

Initially:

- Streamlit (future)

---

# Development Rules

1. Build the smallest working version first.
2. Avoid unnecessary complexity.
3. Do not build a generic chatbot.
4. Do not add agents without a clear purpose.
5. Document important decisions.
6. Keep the architecture stable.
7. Prefer working software over theoretical design.

---

# Git Workflow

- All work happens on feature branches: `feature/quant-agent`
- No commits to `main` without PR review (even when working solo)
- Issues track all work: bugs, features, and research tasks
- Close issues with commit messages such as: `Fixes #7`
- Make small, frequent commits with descriptive messages

---

# Current Project Status

## Stage

Initial Development

### Completed

- Project concept defined
- Architecture designed
- Documentation system created
- GitHub repository initialized

### Current Priorities

1. Create the database foundation
2. Build the first data collector
3. Implement the Quant Agent

---

# Success Criteria

The MVP is successful if:

- A user can analyze an entity.
- The system collects real data.
- Agents produce structured analysis.
- The loop evaluates research quality.
- The system generates a professional investment memo.
- The project demonstrates modern AI engineering practices.