# SPEC.md

# Autonomous Investment Research System (AIRS)

## Product Specification

**Version:** 0.3.7

**Status:** Active Development — Core Loop Complete

---

# 1. Product Overview

## Product Name

## Autonomous Investment Research System (AIRS)

---

## Vision

Build an evidence-driven investment research infrastructure that automates the structured workflow of a professional investment research team.

AIRS collects evidence from multiple sources, audits its own reasoning through deterministic evaluation, and generates transparent, traceable investment research reports. It does not predict prices. It does not provide investment advice. It structures, validates, and reports on publicly available evidence.

---

## 2. Problem Statement

Investment research requires gathering information from many disconnected sources:

- Financial data

- Technical activity

- Company news

- Developer ecosystem signals

- Competitive information

Human analysts spend significant time collecting and organizing information before making investment decisions. Existing AI tools often produce confident-sounding outputs without provenance, hide uncertainty, and suppress contradictions.

AIRS reduces repetitive collection work while maintaining research discipline: evidence tracking, contradiction detection, explicit uncertainty, and deterministic quality evaluation.

---

## 3. Product Goal

A user should be able to:

1. Provide an entity name and optional identifiers (ticker, repository).

2. Run an automated evidence-driven research process.

3. Allow the system to iterate and deepen analysis adaptively.

4. Receive a structured investment research memo with:

- Audit dashboard

- Directional bias + explicit uncertainty

- Evidence-backed bull / bear / base cases

- Risk assessment

- Active questions and unresolved contradictions

- Full evidence provenance

## Example

### Input

```

python main.py --entity AAPL --ticker AAPL --repo apple/swift --hypotheses --pdf
```
## Output

- Markdown investment memo (reports/output/AAPL_20260805_043449.md)

- Optional PDF investment memo (reports/output/AAPL_20260805_043449.pdf)

- Console dashboard with halt reason, directional bias, uncertainty, and active questions

# 4. Target Users

## Primary Users

- Investment researchers

- Quantitative analysts

- Due diligence professionals

## Secondary Users

- Startup founders evaluating markets

- Developers interested in financial intelligence workflows

- Technology investors assessing open-source ecosystems

# 5. Supported Scope

AIRS focuses on **research assistance and evidence organization**.

AIRS does **NOT**:

- Provide financial advice

- Execute trades

- Predict future prices

- Manage portfolios

- Output normalized probabilities or fake confidence percentages

# 6. Supported Entity Types

## Public Companies

Examples: NVIDIA, Tesla, Apple

Available dimensions:

- Market data (via yfinance)

- News (via RSS)

- GitHub repository (optional)

## Cryptocurrencies

Examples: Bitcoin, Ethereum

Available dimensions:

- Market data (via yfinance)

- News (via RSS)

- GitHub repository (optional)

## Open-Source Ecosystems / Pre-Launch Projects

Examples: rust-lang, emerging protocols

Available dimensions:

- News (via RSS)

- GitHub repository

- Quantitative analysis skipped when no ticker is provided

# 7. Asset Type Detection

The system probes inputs at runtime and classifies the asset:

| **Asset Type** | **Trigger** | **Active Dimensions** |
| --- | --- | --- |
| public_stock_with_repo | --ticker + --repo provided | Quant, Business, Technical |
| public_stock | --ticker only | Quant, Business |
| open_source_or_pre_launch | --repo only (no ticker) | Business, Technical |
| business_only | --entity only | Business |

Skipped dimensions are recorded as "skipped" in the Evidence Register, not as failures.

# 8. Core User Flow

## Step 1: User Input

```bash
python main.py --entity [name] --ticker [symbol] --repo [owner/repo] --hypotheses
```

## Step 2: Capability Probe

The system detects which research dimensions are available based on provided CLI arguments.

## Step 3: Bootstrap

Business Agent and Technical Agent execute once:

- Business Agent: RSS news collection + Ollama summarization

- Technical Agent: GitHub REST API analysis

Both write findings to the Evidence Register.

## Step 4: Iterative Evidence Accumulation

Quant Agent executes in tiers:

- **Tier 1:** 3-month data depth

- **Tier 2:** 6-month data depth

- **Tier 3:** 1-year data depth

After each tier, the Critic Agent evaluates evidence quality and decides whether to continue.

Maximum iterations: **3**

## Step 5: Quality Evaluation (Critic Agent)

The Critic Agent evaluates through a 6-phase pipeline:

1. **Inventory** — Catalog available evidence

2. **Directional Signals** — Extract bullish, bearish, neutral signals per dimension

3. **Dashboard** — Compute Data Quality, Coverage, Agreement, Stability

4. **Contradictions** — Execute 12 hardcoded cross-agent contradiction rules

5. **Active Questions** — Generate specific research questions

6. **Halt Decision** — Iteration-aware stopping logic

Halt conditions:

- Iteration 1: Coherent directional view formed

- Iteration 2: Thesis stable across iterations

- Iteration 3: Circuit breaker (max iterations)

## Step 6: Hypothesis Generation

The Hypothesis Engine reads from the Evidence Register and produces:

- **Directional Bias:** Bullish strength vs. Bearish strength (raw evidence weights)

- **Uncertainty:** Separate score (Scarcity + Conflict + Coverage)

- **Bull / Bear / Base Cases:** Each with traceable evidence claims

No normalization to 100%. No artificial probability floors.

## Step 7: Risk Assessment

The Risk Agent performs deterministic downside analysis:

- Risk factors with severity classification

- Cross-agent contradiction detection

- Blind-spot warnings

## Step 8: Report Generation

The Report Generator produces a professional investment memo:

- Jinja2-templated Markdown

- 7 sections: Executive Summary, Audit Dashboard, Investment Thesis, Evidence Register Summary, Risk Assessment, Active Questions & Unresolved Contradictions, Appendix

- Optional PDF export via --pdf

- Deterministic data formatting (no LLM for tables or numbers)

# 9. Functional Requirements

## FR-001: Entity Input

The system must accept an entity name and optional identifiers via the command line.

```bash
python main.py --entity "AAPL" --ticker "AAPL" --repo "apple/swift" --hypotheses
```

## FR-002: Market Analysis

The Quant Agent must calculate:

- Historical performance (daily, weekly, monthly returns)

- Volatility (annualized standard deviation)

- Momentum (5d, 10d, 20d, 30d)

- Risk indicators (drawdown, risk score, trend)

- Technical indicators (RSI, MACD, ATR, volume profile)

- Systematic risk (beta, correlation matrix)

All calculations are deterministic. No LLM involvement.

## FR-003: Technical Analysis

The Technical Agent must analyze:

- Developer activity (commit frequency, contributor count)

- Repository health (health score, days since last commit, open issues)

- Maintenance signals

Uses raw requests to GitHub REST API. LLM used only for summary generation.

## FR-004: Business Analysis

The Business Agent must:

- Fetch RSS news feeds

- Summarize articles using Ollama

- Extract structured signals (positive, negative, neutral)

- Identify catalysts and risks

- Output confidence breakdown with provenance

## FR-005: Research Loop

The system must:

- Evaluate research quality via rule-based Critic Agent

- Identify missing information through Active Questions

- Iterate up to three times with deepening quantitative data

- Halt early when evidence is coherent

- Generate a best-effort report if the maximum iteration count is reached

## FR-006: Report Generation

The system must generate a structured investment memo containing:

## Required Sections

1. **Executive Summary** — Directional bias, uncertainty level, halt reason

2. **Audit Dashboard** — Data Quality, Coverage, Agreement, Stability scores

3. **Investment Thesis**

    - Bull Case (evidence table: description, source, strength, raw value)

    - Bear Case (evidence table)

    - Base / Neutral Case (evidence table)

    - Uncertainty Analysis (scarcity, conflict, coverage breakdown)

4. **Evidence Register Summary**

    - Evidence by Source

    - Evidence by Tier

    - Quantitative Evidence (full metrics)

    - Business Evidence (signals, catalysts, risks)

    - Technical Evidence (health metrics)

5. **Risk Assessment** — Severity-classified risks and warnings

6. **Active Questions & Unresolved Contradictions**

7. **Appendix** — Methodology, design principles, limitations, disclaimer

## Technical Requirements

- Jinja2 templating (reports/templates/report.md.j2)

- Deterministic data formatting (no LLM for numbers or tables)

- Markdown output saved to reports/output/

- Optional PDF export via --pdf flag

- Graceful fallback if WeasyPrint is unavailable

- Every claim cites source agent, computation tier, and raw value

## FR-007: Evidence Register

The system must maintain a central Evidence Register with:

- Provenance tracking (source agent, tier, data points, data period, timestamp)

- Trustworthiness validation

- Snapshot support

- Query interface (add, get, has, snapshot, list_by_source, list_by_tier)

## FR-008: Audit Dashboard

The Critic Agent must produce a four-dimensional dashboard:

| **Dimension** | **Description** |
| --- | --- |
| Data Quality | Statistical soundness of available metrics |
| Coverage | Percentage of applicable dimensions/features present |
| Agreement | Whether active dimensions agree on directional signal |
| Stability | Whether deeper data changed the thesis across iterations |

# 10. Non-Functional Requirements

## Cost

Development cost target: **$0**

No paid APIs are required.

## Performance

The system should complete a basic analysis within **5 minutes** on the target hardware:

- NVIDIA GTX 1060 (6 GB)

- 16 GB RAM

Business Agent Ollama calls may take 60-90s per prompt on consumer hardware.

## Maintainability

The system must remain modular.

New analysis modules should be added without rewriting the overall architecture.

## Transparency

Reports must clearly show:

- Evidence used

- Sources

- Reasoning behind conclusions

- Explicit uncertainty (independent from directional bias)

- Halt reason

## Error Handling

The system must handle:

- API timeouts (retry 3 times, then use cached data)

- Empty data (log a warning and continue with partial analysis)

- LLM unavailable (fall back to rule-based analysis and reduce confidence)

- Rate limits (use fallback mechanisms and flag limitations)

- Missing CLI arguments (gracefully skip unavailable agents, record as "skipped")

# 11. Technical Constraints

## Hardware

| **Component** | **Specification** |
| --- | --- |
| GPU | NVIDIA GTX 1060 6 GB |
| RAM | 16 GB |
| OS | Windows 10 / Linux / macOS |
| Development Cost | $0 |

## Technology Choices

| **Category** | **Technology** |
| --- | --- |
| Backend | Python 3.11+ |
| Database | SQLite |
| AI Runtime | Ollama |
| Models | Qwen 2.5 7B, Llama 3.1 8B, Mistral 7B |
| Templating | Jinja2 |
| PDF Export | WeasyPrint (optional) |
| Frontend | Streamlit (future — Phase 10) |

# 12. Data Models

## Evidence Item Format

```python
{

"key": "returns",

"value": {"daily_mean": 0.1841, "weekly": -8.31, "monthly": 0.09},

"source": "quant_agent",

"tier": 1,

"data_points": 63,

"data_period": "3mo",

"timestamp": "2026-08-05T04:34:00Z"

}
```

## Agent Output Format

All agents return a standardized dictionary.

```python
{

"agent": "quant",

"entity": "AAPL",

"timestamp": "2026-08-05T04:34:00Z",

"metrics": {

"trend": "downtrend",

"volatility": 0.2585,

"momentum": {"20d": -0.0120},

"risk_score": 0.3043

},

"confidence": 0.78,

"status": "complete", *# "complete", "partial", "failed", "skipped"*

"sources": ["yfinance"]

}
```

## Critic Output Format

```python
{

"dashboard": {

"data_quality": {"score": 0.78, "details": "quant, business, technical"},

"coverage": {"score": 1.00, "details": "18/18 features present"},

"agreement": {"level": "Low", "details": "1 positive, 1 negative, 2 neutral"},

"stability": {"level": "Stable", "details": "No dimension flipped direction"}

},

"active_questions": [

{

"question": "Which dimension is the leading indicator?",

"why_it_matters": "Dimensions disagree",

"can_deeper_data_answer": True

}

],

"contradictions": [...],

"halt": False,

"halt_reason": "insufficient_clarity"

}
```

## Hypothesis Output Format

```python
{

"directional_bias": {

"bull_strength": 1.21,

"bear_strength": 2.91,

"directional_score": -1.70,

"net": "bearish"

},

"uncertainty": {

"score": 0.17,

"level": "Low",

"factors": {

"scarcity": 0.00,

"conflict": 0.17,

"coverage": 0.00

}

},

"bull": {

"thesis": "AAPL is undervalued with upside potential",

"claims": [...],

"total_strength": 1.21,

"evidence_count": 3

},

"bear": {...},

"base": {...}

}
```

## Loop State Format

```python
{

"entity": "AAPL",

"iteration": 2,

"max_iterations": 3,

"asset_type": "public_stock_with_repo",

"evidence_register": {...},

"critic_output": {...},

"dashboard_history": [...],

"status": "iterating" *# "iterating", "complete", "failed"*

}
```

# 13. MVP Success Criteria

## User Experience

A user can:

- Enter an entity with optional ticker and repository

- Start research with --hypotheses

- Receive a Markdown report with directional bias, uncertainty, and evidence tables

- Understand why the system halted and what questions remain

## Technical

The system includes:

- [x] Data collection with retry logic

- [x] Analysis modules (Quant, Technical, Business, Risk)

- [x] Research loop with rule-based critique

- [x] LLM integration for qualitative tasks only

- [x] Evidence Register with provenance tracking

- [x] Hypothesis Engine with directional bias + uncertainty

- [x] Jinja2 report generation (Markdown + optional PDF)

## Portfolio Quality

A developer can clearly explain:

- Architecture decisions and agent workflow

- Loop engineering design and halt logic

- Why directional bias replaces probability normalization

- Evidence Register as single source of truth

- Cost optimization ($0 paid APIs)

- Engineering tradeoffs (local LLMs vs. speed, heuristic thresholds vs. calibration)

# 14. Future Features

The following are **not** part of the v0.3.7 MVP:

- Audit Trail & Backtesting (Phase 9 — Active)

- Streamlit web interface (Phase 10 — Planned)

- Real-time monitoring

- Portfolio tracking

- Alerts

- Automated investment recommendations

- Cloud deployment

- Multi-user support

- Advanced machine learning prediction models

- On-chain data integration

- ESG Agent, Macro Agent

# 15. Product Principles

- **Evidence over opinions.** Every conclusion traces to the Evidence Register.

- **Automation over manual research.** Agents handle collection and structuring.

- **Simplicity over unnecessary complexity.** No feature without clear purpose.

- **Reliable workflows over uncontrolled autonomy.** The loop is bounded and deterministic.

- **LLMs assist reasoning; they do not replace engineering.** No LLM performs calculations or decides halt.

- **Iteration improves quality; one-shot analysis is insufficient.** Adaptive depth based on evidence coherence.

- **Uncertainty is explicit.** It is independent from directional conviction and never hidden.

- **Contradictions are signals.** They are surfaced, not averaged away.

<div align="center">

## AIRS v0.3.7

## Evidence-Driven Investment Research Infrastructure

</div> 