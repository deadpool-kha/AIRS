# AIRS Evaluation Framework

> **Version:** 0.3.7  
> **Last Updated:** 2026-08-05

---

# Purpose

AIRS is **not evaluated by its ability to predict future prices.**

Instead, it is evaluated on the quality, transparency, and auditability of its research process.

The objective is to determine whether AIRS consistently produces structured, evidence-based investment research that can be inspected, reproduced, and improved over time.

---

# Evaluation Philosophy

A successful research system should answer questions such as:

- Did it collect sufficient evidence?
- Is every conclusion traceable?
- Were contradictions identified?
- Was uncertainty communicated honestly?
- Can another researcher reproduce the analysis?

Prediction accuracy is a **future validation metric** (Phase 9).

Research quality is the **primary evaluation metric** today.

---

# Evaluation Criteria

The current framework evaluates AIRS across five major dimensions.

---

# 1. Evidence Completeness

Every research session should gather evidence from all applicable research dimensions.

## Success Criteria

| Component | Pass Criteria |
|-----------|---------------|
| **Quant Agent** | Computes returns, volatility, momentum, trend, drawdown, and risk score |
| **Business Agent** | Extracts at least one meaningful signal from current news |
| **Technical Agent** | Produces repository health metrics when a GitHub repository is supplied |
| **Evidence Register** | Stores every observation with source, timestamp, and provenance |

---

## Goal

The system should maximize evidence coverage before generating hypotheses.

Missing evidence should be reported—not ignored.

---

# 2. Provenance & Auditability

Every statement appearing in the final report must be traceable.

Each claim should identify:

- Source agent
- Computation tier
- Data collection period
- Original evidence value

---

## Required Provenance

| Attribute | Example |
|-----------|---------|
| Source Agent | Quant Agent |
| Computation Tier | Tier 2 |
| Data Period | 6 Months |
| Raw Evidence | Volatility = 23.7% |

---

## Goal

Every conclusion should support the chain:

```text
Conclusion
      │
      ▼
Evidence
      │
      ▼
Original Source
      │
      ▼
Reasoning
```

Nothing should appear in a report without an identifiable origin.

---

# 3. Contradiction Detection

Markets rarely provide perfectly consistent signals.

AIRS intentionally evaluates whether different research dimensions disagree.

---

## Examples

| Situation | Expected Outcome |
|-----------|------------------|
| Rising price + negative business sentiment | Flag contradiction |
| Strong GitHub activity + weak financial indicators | Flag contradiction |
| Positive news + elevated downside risk | Flag contradiction |
| High momentum + deteriorating fundamentals | Flag contradiction |

---

## Goal

Contradictions should be surfaced—not averaged away.

Disagreement is often where the most valuable research begins.

---

# 4. Uncertainty Calibration

Uncertainty measures how complete and reliable the available evidence is.

It is **not** the inverse of confidence.

---

## Expected Behavior

| Situation | Expected Uncertainty |
|-----------|---------------------|
| Limited evidence coverage | High |
| Strong disagreement across dimensions | High |
| Deep evidence with broad agreement | Low |
| Perfect certainty | Never allowed |

---

## Guiding Principle

Every research conclusion should retain a degree of epistemic humility.

There is always some uncertainty.

---

# 5. Report Quality

Every generated investment memo should follow a consistent professional structure.

---

## Required Sections

- Executive Summary
- Audit Dashboard
- Investment Thesis
  - Bull Case
  - Bear Case
  - Base Case
- Evidence Register Summary
- Risk Assessment
- Active Questions
- Methodology
- Design Principles
- Limitations
- Disclaimer

---

## Report Requirements

A high-quality report should:

- Clearly explain the research outcome
- Reference supporting evidence
- Communicate uncertainty
- Highlight unresolved contradictions
- Remain understandable without reading the source code

---

# Manual Validation

The following scenarios should be tested after significant architectural changes.

---

## Test Case 1 — Public Equity

### Command

```bash
python main.py --entity AAPL --ticker AAPL --hypotheses
```

### Expected Behavior

- Quant Agent executes
- Business Agent executes
- Technical Agent skipped
- Halt after Iteration 1–2
- Markdown report generated
- Directional hypothesis produced

---

## Test Case 2 — Cryptocurrency with Repository

### Command

```bash
python main.py \
    --entity bitcoin \
    --ticker BTC-USD \
    --repo bitcoin/bitcoin \
    --hypotheses
```

### Expected Behavior

- All three research dimensions active
- Higher evidence count
- Possible additional iteration due to conflicting market signals
- Complete investment report generated

---

## Test Case 3 — Open Source Project

### Command

```bash
python main.py \
    --entity rust-lang \
    --repo rust-lang/rust \
    --hypotheses
```

### Expected Behavior

- Quant Agent skipped
- Technical Agent executes
- Business Agent executes
- Asset classified as `open_source_or_pre_launch`
- Research completes without requiring market data

---

## Test Case 4 — Partial Input

### Command

```bash
python main.py --entity AAPL --hypotheses
```

### Expected Behavior

- Business Agent searches using entity name
- Technical Agent skipped
- Quant Agent skipped (no ticker)
- Pipeline completes successfully
- No runtime errors

---

# Success Checklist

A successful research session should satisfy the following.

| Requirement | Pass |
|-------------|:----:|
| Evidence collected | ✅ |
| Provenance tracked | ✅ |
| Contradictions identified | ✅ |
| Uncertainty calculated | ✅ |
| Professional report generated | ✅ |
| Pipeline completed without failure | ✅ |

---

# Future Evaluation (Phase 9)

Phase 9 introduces historical validation through the Audit Trail.

Every completed research session will be stored for future evaluation.

---

## Planned Workflow

```text
Research Session
        │
        ▼
Save Evidence Snapshot
        │
        ▼
Wait 30 Days
        │
        ▼
Fetch Actual Market Outcome
        │
        ▼
Compare Against Original Hypothesis
        │
        ▼
Compute Historical Accuracy
```

---

## Metrics to Measure

The Audit Trail will evaluate:

- Directional bias accuracy
- Accuracy by asset type
- Accuracy by uncertainty level
- Accuracy by evidence coverage
- Accuracy by signal combination
- Long-term research consistency

This allows AIRS to evaluate whether its research process produces useful long-term outcomes.

---

# Current Limitations

The evaluation framework currently has several known limitations.

## Business Agent

- RSS feeds provide live news only.
- Historical news archives are not yet integrated.

---

## Technical Agent

- Repository evaluation uses a single snapshot.
- Historical repository evolution is not yet considered.

---

## Hypothesis Engine

- Directional strength thresholds are heuristic.
- They have not yet been calibrated using historical performance data.

---

## Test Coverage

The most comprehensive end-to-end testing has been performed on **public equities**.

Additional validation is planned for:

- Cryptocurrencies
- Open-source ecosystems
- Private companies
- Startup research workflows

---

# Future Vision

As AIRS evolves, evaluation will shift from:

> **"Did the system generate a convincing report?"**

to

> **"Did the research process consistently produce reliable, evidence-supported conclusions over time?"**

This transition—from subjective evaluation to measurable historical performance—is the foundation of the Audit Trail and Backtesting system planned for Phase 9.

---

<div align="center">

# AIRS v0.3.7

**Evidence-Driven Investment Research Infrastructure**

*"Research quality comes before prediction accuracy."*

</div>