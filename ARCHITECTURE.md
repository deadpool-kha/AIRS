# ARCHITECTURE.md

# Autonomous Investment Research System (AIRS)

## Purpose

This document explains the technical architecture of the system.

The goal is to build a modular AI research platform that collects information, analyzes evidence, evaluates quality, and generates investment research reports.

---

# System Overview

The system has five major layers:

```
                 User
                  |
                  |
            Research Request
                  |
                  v

        Research Controller Layer

                  |
     --------------------------------
     |              |               |
     v              v               v

 Data Layer   Agent Layer    Intelligence Layer

     |              |               |

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

Sources:

* financial APIs
* GitHub API
* RSS feeds
* public documents

Responsibilities:

* data collection
* cleaning
* normalization
* storage

---

# Layer 2: Database Layer

Initial database:

SQLite

Stores:

* entities
* historical market data
* technical activity
* news
* research states
* reports

---

# Layer 3: Agent Layer

Agents are specialized modules.

## Quant Agent

Handles numerical analysis.

Input:

Market data

Output:

* trend
* volatility
* momentum
* risk metrics

## Technical Agent

Handles engineering ecosystem analysis.

Input:

GitHub data

Output:

* developer activity
* project health
* maintenance signals

## Business Agent

Handles company activity.

Input:

News and public information

Output:

* catalysts
* business signals

## Risk Agent

Finds weaknesses.

Output:

* risks
* concerns
* uncertainty

---

# Layer 4: Loop Controller

The loop controller manages workflow execution.

Responsibilities:

* maintain state
* decide next action
* track completion
* call required agents

The loop follows:

```
Goal

↓

Planning

↓

Research

↓

Analysis

↓

Evaluation

↓

Completion
```

---

# Layer 5: LLM Layer

LLMs are used for:

* planning
* reasoning
* critique
* writing

LLMs are NOT used for:

* calculations
* simple data processing
* database tasks

---

# Design Principles

1. Modular components
2. Local-first development
3. Minimize API costs
4. Human-readable outputs
5. Evidence-based conclusions
