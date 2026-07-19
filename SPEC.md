# SPEC.md

# Autonomous Investment Research System (AIRS)

## Product Specification

Version:

0.1 MVP

Status:

Development Planning

---

# 1. Product Overview

## Product Name

Autonomous Investment Research System (AIRS)

---

## Vision

Build an AI-assisted investment research platform that automates the early stages of investment analysis.

The system should help users quickly understand a company, protocol, or technology by collecting evidence from multiple sources, analyzing signals, identifying risks, and generating a structured research report.

---

# 2. Problem Statement

Investment research requires gathering information from many disconnected sources:

* financial data
* technical activity
* company news
* developer ecosystem signals
* competitive information

Human analysts spend significant time collecting and organizing information before making decisions.

AIRS aims to reduce this repetitive work by creating an automated research workflow.

---

# 3. Product Goal

The MVP should allow a user to:

1. Select an entity.
2. Run an automated research process.
3. Receive a structured investment research report.

Example:

Input:

```
Analyze NVIDIA
```

Output:

```
Investment Research Report

Overview

Quantitative Analysis

Technical Analysis

Business Signals

Risk Factors

Key Questions

Summary
```

---

# 4. Target Users

Primary:

Investment researchers

Secondary:

* startup founders
* analysts
* developers interested in financial intelligence
* technology investors

---

# 5. MVP Scope

The MVP focuses on research assistance.

The MVP does NOT:

* provide financial advice
* execute trades
* predict future prices
* manage portfolios

The goal is evidence organization and analysis.

---

# 6. Supported Entity Types

Initial support:

## Public Companies

Examples:

* NVIDIA
* Tesla

Available information:

* market data
* news
* business information

## Crypto Projects

Examples:

* Ethereum
* Solana

Available information:

* market data
* developer activity
* ecosystem signals

## AI Companies

Examples:

* AI infrastructure companies
* open-source AI projects

Available information:

* technical activity
* public announcements
* ecosystem growth

---

# 7. Core User Flow

## Step 1: User Input

User enters:

```
Analyze [entity]
```

---

## Step 2: Research Planning

System creates a research plan.

Example:

Need:

* market analysis
* technical analysis
* business information
* risk assessment

---

## Step 3: Data Collection

System collects:

* market data
* GitHub activity
* public information

---

## Step 4: Analysis

Specialized modules analyze collected information.

Modules:

* Quant Analysis
* Technical Analysis
* Business Analysis
* Risk Analysis

---

## Step 5: Quality Evaluation

A critic component evaluates:

* Is enough evidence collected?
* Are important risks considered?
* Are conclusions supported?

If not:

The system continues research.

---

## Step 6: Report Generation

The system creates:

Investment Research Memo

---

# 8. Functional Requirements

## FR-001: Entity Input

The system must accept an entity name.

Example:

```
Ethereum
```

---

## FR-002: Market Analysis

The system must calculate:

* historical performance
* volatility
* momentum
* risk indicators

---

## FR-003: Technical Analysis

The system must analyze:

* developer activity
* repository health
* contribution trends

---

## FR-004: Risk Analysis

The system must identify:

* negative signals
* uncertainty
* possible weaknesses

---

## FR-005: Report Generation

The system must generate a structured report.

---

# 9. Non-Functional Requirements

## Cost

Development cost target:

$0

No required paid APIs.

---

## Performance

The system should complete a basic analysis within reasonable time on local hardware.

---

## Maintainability

The system should be modular.

New analysis modules should be added without rewriting the entire system.

---

## Transparency

Reports should show:

* evidence used
* sources
* reasoning behind conclusions

---

# 10. Technical Constraints

Hardware:

GPU:

NVIDIA GTX 1060 6GB

RAM:

16GB

Operating System:

Windows 10

Development environment:

Local-first.

---

# 11. Technology Choices

Backend:

Python

Database:

SQLite

AI Runtime:

Ollama

Models:

* Qwen
* Llama
* Mistral

Frontend:

Streamlit initially.

---

# 12. MVP Success Criteria

The MVP is complete when:

## User Experience

A user can:

* enter an entity
* start research
* receive a report

## Technical

The system has:

✓ Data collection

✓ Analysis modules

✓ Research loop

✓ LLM integration

✓ Report generation

## Portfolio Quality

A developer can explain:

* architecture decisions
* agent workflow
* cost optimization
* engineering tradeoffs

---

# 13. Future Features

Not part of MVP:

* real-time monitoring
* portfolio tracking
* alerts
* automated investment recommendations
* cloud deployment
* multi-user support
* advanced ML prediction models

---

# 14. Product Principles

1. Evidence over opinions.
2. Automation over manual research.
3. Simplicity over unnecessary complexity.
4. Reliable workflows over uncontrolled autonomy.
5. LLMs assist reasoning; they do not replace engineering.
