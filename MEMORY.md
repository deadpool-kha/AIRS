# MEMORY.md

# Project: Autonomous Investment Research System (AIRS)

## Role of This Document

This file provides the complete context of the project for AI assistants and developers.

When assisting with this project:

* Understand the architecture before suggesting changes.
* Do not redesign the system unless explicitly requested.
* Prefer simple, reliable engineering solutions.
* Explain tradeoffs behind technical decisions.
* Prioritize completing the MVP.

---

# Project Goal

Build an AI-powered investment research system that automates the workflow of an investment research team.

The system should analyze:

1. Public companies

   * Example: NVIDIA, Tesla

2. Crypto protocols/assets

   * Example: Ethereum, Solana

3. AI companies/startups

   * Using publicly available information

The goal is NOT to predict stock or crypto prices.

The goal is to create structured, evidence-based research reports.

---

# Why This Project Exists

This project is being built as:

1. A portfolio project for AI/software engineering roles.
2. A demonstration of modern AI engineering skills.
3. A practical exploration of investment research automation.

The project combines:

* AI agents
* loop engineering
* quantitative analysis
* data engineering
* financial research workflows

---

# Core Product Vision

User provides:

"Analyze [entity]"

Example:

"Analyze NVIDIA"

The system performs an investment committee workflow:

1. Collect evidence
2. Analyze data
3. Evaluate risks
4. Critique the research
5. Generate a final research memo

---

# Important Engineering Principle

Do NOT use LLMs for everything.

Use traditional programming for:

* calculations
* metrics
* data processing
* database operations
* deterministic analysis

Use LLMs for:

* planning
* reasoning
* critique
* summarization
* final report generation

The LLM is a reasoning layer, not the entire system.

---

# High-Level Architecture

```
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

Potential sources:

### Market Data

Examples:

* Yahoo Finance
* CoinGecko
* other free market APIs

Data:

* price
* volume
* returns
* volatility

### Technical Data

Source:

* GitHub API

Data:

* commits
* contributors
* releases
* issues

### Business Data

Sources:

* RSS feeds
* company websites
* public announcements

Data:

* partnerships
* funding
* product launches
* important events

---

# 2. Database Layer

Initial database:

SQLite

Future possibility:

PostgreSQL

Stores:

* entities
* market data
* GitHub activity
* news
* research results
* agent states

---

# 3. Agents

Agents are specialized modules.

They are NOT separate ChatGPT conversations.

---

## Quant Agent

Purpose:

Analyze numerical information.

Responsibilities:

* price trends
* returns
* volatility
* momentum
* drawdown
* risk metrics

Implementation:

Python

Libraries:

* pandas
* numpy
* statistics libraries

No LLM required.

---

## Technical Agent

Purpose:

Analyze technical ecosystem health.

Data:

GitHub activity.

Metrics:

* contributor growth
* commit frequency
* release activity
* project maintenance

Implementation:

Python.

---

## Business Agent

Purpose:

Analyze qualitative business information.

Inputs:

* news
* announcements
* public information

May use local LLM.

---

## Risk Agent

Purpose:

Find weaknesses and negative signals.

Examples:

* competition
* regulatory concerns
* declining activity
* high risk factors

Uses:

* rules
* data analysis
* LLM reasoning when useful

---

## Critic Agent

Purpose:

Evaluate research quality.

Before generating the final report, it checks:

* Is enough evidence collected?
* Are claims supported?
* Are risks considered?
* Is information missing?

If research is incomplete:

The loop continues.

---

# Loop Engineering Design

The system uses a controlled research loop.

The loop:

```
Receive Goal

↓

Create Research Plan

↓

Collect Evidence

↓

Run Analysis Agents

↓

Evaluate Research Quality

↓

Missing Information?

YES:
Continue Research

NO:
Generate Final Report
```

The loop controller decides workflow progression.

The LLM does not control everything.

---

# LLM Architecture

Local-first approach.

No paid APIs during development.

Runtime:

Ollama

Possible models:

* Qwen 2.5 7B
* Llama 3.1 8B
* Mistral 7B

LLM responsibilities:

* planning
* reasoning
* critique
* writing reports

---

# Hardware Environment

Development machine:

GPU:

NVIDIA GTX 1060 6GB

RAM:

16GB

Operating System:

Windows 10

Constraint:

Development cost target:

$0

---

# Technology Stack

Backend:

Python

FastAPI

Database:

SQLite

AI Runtime:

Ollama

Vector Search:

FAISS or ChromaDB

Frontend:

Initially:

Streamlit

Future:

React/Next.js

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

# Current Project Status

Stage:

Planning / Initial Development

Completed:

* Project concept defined
* Architecture designed
* Documentation system created

Current priorities:

1. Create repository
2. Setup Python environment
3. Build database foundation
4. Build first data collector
5. Implement Quant Agent

---

# How AI Assistants Should Help

Act as a senior software engineer.

Before providing code:

1. Understand the existing architecture.
2. Check current project status.
3. Avoid unnecessary rewrites.
4. Explain why a solution is chosen.

The developer makes final architectural decisions.

---

# Success Criteria

The MVP is successful if:

* A user can analyze an entity.
* The system collects real data.
* Agents produce structured analysis.
* The loop evaluates research quality.
* The system generates a professional investment memo.
* The project demonstrates modern AI engineering practices.
