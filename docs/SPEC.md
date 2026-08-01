# SPEC.md

# Autonomous Investment Research System (AIRS)

## Product Specification

**Version:** 0.1 MVP  
**Status:** Development Planning

---

# 1. Product Overview

## Product Name

**Autonomous Investment Research System (AIRS)**

---

## Vision

Build an AI-assisted investment research platform that automates the early stages of investment analysis.

The system helps users quickly understand a company, protocol, or technology by collecting evidence from multiple sources, analyzing signals, identifying risks, and generating a structured research report.

The system uses **loop engineering**, allowing it to critique its own research and iterate to improve report quality.

---

# 2. Problem Statement

Investment research requires gathering information from many disconnected sources, including:

- Financial data
- Technical activity
- Company news
- Developer ecosystem signals
- Competitive information

Human analysts spend significant time collecting and organizing information before making investment decisions.

AIRS aims to reduce this repetitive work by creating an automated research workflow with built-in quality control.

---

# 3. Product Goal

The MVP should allow a user to:

1. Select an entity.
2. Run an automated research process.
3. Allow the system to iterate and improve research quality.
4. Receive a structured investment research report.

## Example

### Input

```text
Analyze NVIDIA
```

### Output

```text
Investment Research Report

Overview
Quantitative Analysis
Technical Analysis
Business Signals
Risk Factors
Key Questions

Confidence Level: 85%
Iteration Count: 2

Summary
```

---

# 4. Target Users

## Primary Users

- Investment researchers

## Secondary Users

- Startup founders
- Analysts
- Developers interested in financial intelligence
- Technology investors

---

# 5. MVP Scope

The MVP focuses on **research assistance**.

The MVP does **NOT**:

- Provide financial advice
- Execute trades
- Predict future prices
- Manage portfolios

The goal is evidence organization and analysis.

---

# 6. Supported Entity Types

## Public Companies

Examples:

- NVIDIA
- Tesla

Available information:

- Market data
- News
- Business information

---

## Crypto Projects

Examples:

- Ethereum
- Solana
- Stacks

Available information:

- Market data
- Developer activity
- Ecosystem signals

---

## AI Companies

Examples:

- AI infrastructure companies
- Open-source AI projects

Available information:

- Technical activity
- Public announcements
- Ecosystem growth

---

# 7. Core User Flow

## Step 1: User Input

```text
Analyze [entity]
```

---

## Step 2: Research Planning

The system creates a research plan.

Example tasks:

- Market analysis
- Technical analysis
- Business information gathering
- Risk assessment

---

## Step 3: Data Collection

The system collects:

- Market data
- GitHub activity
- Public information

---

## Step 4: Analysis

Specialized modules analyze the collected information.

Modules:

- Quant Analysis
- Technical Analysis
- Business Analysis
- Risk Analysis

---

## Step 5: Quality Evaluation (Critic Agent)

The Critic Agent evaluates:

- Is enough evidence collected?
- Are important risks considered?
- Are conclusions supported?

If not, the system continues research with targeted iteration.

Maximum iterations: **3**

---

## Step 6: Report Generation

The system generates an **Investment Research Memo** containing:

- Structured findings
- Confidence level
- Iteration count

---

# 8. Functional Requirements

## FR-001: Entity Input

The system must accept an entity name via the command line.

Example:

```bash
python main.py --entity "NVIDIA"
```

---

## FR-002: Market Analysis

The system must calculate:

- Historical performance
- Volatility
- Momentum
- Risk indicators

---

## FR-003: Technical Analysis

The system must analyze:

- Developer activity
- Repository health
- Contribution trends

---

## FR-004: Risk Analysis

The system must identify:

- Negative signals
- Uncertainty
- Possible weaknesses

---

## FR-005: Research Loop

The system must:

- Evaluate research quality
- Identify missing information
- Iterate up to three times
- Generate a best-effort report if the maximum iteration count is reached

---

## FR-006: Report Generation

The system must generate a structured report containing:

- Outputs from all agents
- Confidence level
- Iteration count
- Sources cited

---

# 9. Non-Functional Requirements

## Cost

Development cost target:

**$0**

No paid APIs are required.

---

## Performance

The system should complete a basic analysis within **5 minutes** on the target hardware:

- NVIDIA GTX 1060 (6 GB)
- 16 GB RAM

---

## Maintainability

The system should remain modular.

New analysis modules should be added without rewriting the overall architecture.

---

## Transparency

Reports should clearly show:

- Evidence used
- Sources
- Reasoning behind conclusions
- Confidence levels

---

## Error Handling

The system must handle:

- API timeouts (retry 3 times, then use cached data)
- Empty data (log a warning and continue with partial analysis)
- LLM unavailable (fall back to rule-based analysis and reduce confidence)
- Rate limits (use fallback mechanisms and flag limitations)

---

# 10. Technical Constraints

## Hardware

**GPU**

- NVIDIA GTX 1060 6 GB

**RAM**

- 16 GB

**Operating System**

- Windows 10

**Development Environment**

- Local-first

**Development Cost Target**

- $0

---

# 11. Technology Choices

## Backend

- Python

## Database

- SQLite

## AI Runtime

- Ollama

## Models

- Qwen 2.5 7B
- Llama 3.1 8B
- Mistral 7B

## Frontend

- Streamlit (future)

---

# 12. Data Models

## Agent Output Format

All agents return a standardized dictionary.

```python
{
    "agent": "quant",
    "entity": "AAPL",
    "timestamp": "2026-07-20T15:02:00Z",
    "metrics": {
        "trend": "positive",
        "volatility": 0.25,
        "momentum": 0.15
    },
    "confidence": 0.85,
    "status": "complete",  # "partial" or "failed"
    "sources": ["yfinance"]
}
```

---

## Critic Output Format

```python
{
    "overall_quality": "partial",
    "gaps": [
        "missing_volatility_deep_dive",
        "insufficient_github_data"
    ],
    "recommendations": [
        "Re-run Quant Agent with focus on volatility",
        "Expand GitHub search to related repositories"
    ],
    "should_iterate": True
}
```

---

## Loop State Format

```python
{
    "entity": "AAPL",
    "iteration": 2,
    "max_iterations": 3,
    "agent_outputs": {...},
    "critic_feedback": {...},
    "status": "iterating"  # "complete" or "failed"
}
```

---

# 13. MVP Success Criteria

## User Experience

A user can:

- Enter an entity
- Start research
- Receive a report with a confidence level

---

## Technical

The system includes:

- ✓ Data collection
- ✓ Analysis modules
- ✓ Research loop with critique
- ✓ LLM integration
- ✓ Report generation

---

## Portfolio Quality

A developer can clearly explain:

- Architecture decisions
- Agent workflow
- Loop engineering design
- Cost optimization
- Engineering tradeoffs

---

# 14. Future Features

The following are **not** part of the MVP:

- Real-time monitoring
- Portfolio tracking
- Alerts
- Automated investment recommendations
- Cloud deployment
- Multi-user support
- Advanced machine learning prediction models
- On-chain data integration

---

# 15. Product Principles

- Evidence over opinions.
- Automation over manual research.
- Simplicity over unnecessary complexity.
- Reliable workflows over uncontrolled autonomy.
- LLMs assist reasoning; they do not replace engineering.
- Iteration improves quality; one-shot analysis is insufficient.