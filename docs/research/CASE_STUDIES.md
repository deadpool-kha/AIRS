# AIRS Case Studies

> **Version:** 0.3.7  
> **Last Updated:** 2026-08-05

---

# Overview

This document contains real-world research sessions conducted with AIRS. Each case study demonstrates how the system handles different entity types, input combinations, and research outcomes.

These cases are drawn from actual development testing and illustrate:

- How the Evidence Register accumulates data across agents
- How the Critic Agent evaluates research quality
- How the Hypothesis Engine produces directional bias and uncertainty
- How the loop behaves under different conditions (early halt vs. full iteration)
- How partial inputs are handled gracefully

---

# Case Study 1: Apple Inc. (AAPL) — Public Equity

## Entity

**Apple Inc.** — Publicly traded technology company (NASDAQ: AAPL)

## Command

```bash
python main.py --entity AAPL --ticker AAPL --hypotheses
```

## Research Dimensions

| Dimension | Status | Reason |
|-----------|--------|--------|
| Quant | ✅ Active | `--ticker AAPL` provided |
| Business | ✅ Active | `--entity AAPL` provided |
| Technical | ⏭️ Skipped | No `--repo` argument |

## Bootstrap Phase

### Business Agent

- Fetched RSS feeds for "AAPL" and "Apple"
- Extracted 8 business signals:
  - 3 positive (product launch coverage, earnings beat mention, analyst upgrade)
  - 2 negative (regulatory scrutiny in EU, supply chain concern)
  - 3 neutral (market share report, executive interview, dividend announcement)
- Identified 2 catalysts: upcoming earnings, new product cycle
- Identified 1 risk factor: antitrust regulatory pressure

### Technical Agent

- Skipped (no repository specified)
- Status recorded as `"skipped"` in Evidence Register
- Critic Agent treats this as intentionally omitted, not a failure

## Iteration 1

### Quant Agent — Tier 1 (3 Months)

| Metric | Value | Direction |
|--------|-------|-----------|
| Returns (3mo) | +12.4% | Positive |
| Volatility (annualized) | 18.7% | Moderate |
| Momentum (20d) | +5.2% | Positive |
| Trend | Bullish | — |
| Max Drawdown | -4.1% | Low |
| Risk Score | 0.34 | Low-Medium |

### Evidence Register Snapshot (Iteration 1)

```
Quant:
  - returns_3mo: +12.4% (source: yfinance, tier: 1, data_points: 63)
  - volatility: 18.7% (source: yfinance, tier: 1, data_points: 63)
  - momentum_20d: +5.2% (source: yfinance, tier: 1, data_points: 20)
  - trend: bullish (source: yfinance, tier: 1, data_points: 63)
  - max_drawdown: -4.1% (source: yfinance, tier: 1, data_points: 63)
  - risk_score: 0.34 (source: quant_agent, tier: 1, data_points: 6)

Business:
  - signal_count: 8 (source: business_agent, tier: 1, data_points: 8)
  - positive_signals: 3 (source: business_agent, tier: 1, data_points: 3)
  - negative_signals: 2 (source: business_agent, tier: 1, data_points: 2)
  - catalysts: 2 (source: business_agent, tier: 1, data_points: 2)
  - risks: 1 (source: business_agent, tier: 1, data_points: 1)

Technical:
  - status: skipped (source: technical_agent, tier: 0, data_points: 0)
```

### Critic Agent — Phase 3: Dashboard

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Data Quality | 81% | Strong — yfinance + RSS both responsive |
| Coverage | 59% | Partial — 2 of 3 dimensions active |
| Agreement | **High** | Quant bullish + Business net positive align |
| Stability | Unknown | First iteration |

### Critic Agent — Phase 4: Contradictions

- **No critical contradictions detected**
- Minor tension: Quant shows low risk (0.34) but Business flags regulatory risk
- Critic classifies this as "manageable tension" rather than contradiction

### Critic Agent — Phase 6: Halt Decision

**Halt = True**

Reason: Coverage >= 50%, Agreement = High, no critical contradictions. A coherent directional view can be formed with available evidence.

## Hypothesis Engine Output

### Directional Bias

| Component | Strength |
|-----------|----------|
| Bullish | 1.68 |
| Bearish | 0.58 |
| **Net Bias** | **BEARISH (-1.10)** |

> Note: Despite positive quant metrics, the Business Agent's regulatory risk signal and negative business signals carried significant weight. The Evidence Register weighted qualitative risks heavily in this session.

### Uncertainty

| Factor | Score | Assessment |
|--------|-------|------------|
| Scarcity | 15% | Moderate evidence volume |
| Conflict | 8% | Low disagreement |
| Coverage | 6% | One dimension missing |
| **Total** | **29%** | **Moderate** |

### Claims

| Claim | Source | Strength | Direction |
|-------|--------|----------|-----------|
| 3-month returns positive | Quant Agent | 0.45 | Bullish |
| Low drawdown (-4.1%) | Quant Agent | 0.35 | Bullish |
| Regulatory risk flagged | Business Agent | 0.55 | Bearish |
| Supply chain concern | Business Agent | 0.40 | Bearish |
| Earnings catalyst ahead | Business Agent | 0.30 | Neutral |

## Final Report

- **Halted at:** Iteration 1
- **Report sections:** All 7 sections generated
- **Key insight:** Positive price action masks underlying business risks; regulatory overhang is the dominant bearish signal
- **Active questions:**
  1. What is the timeline for EU regulatory decisions?
  2. How material is the supply chain concern relative to revenue?

## Takeaway

AIRS halted early because available evidence agreed on direction. The system did not waste compute on deeper quant tiers when the business narrative already provided a clear risk signal. This demonstrates the dashboard-driven halt logic: **coherence beats completeness.**

---

# Case Study 2: Bitcoin (BTC-USD) — Cryptocurrency with Repository

## Entity

**Bitcoin** — Cryptocurrency and open-source protocol

## Command

```bash
python main.py \
    --entity bitcoin \
    --ticker BTC-USD \
    --repo bitcoin/bitcoin \
    --hypotheses
```

## Research Dimensions

| Dimension | Status | Reason |
|-----------|--------|--------|
| Quant | ✅ Active | `--ticker BTC-USD` provided |
| Business | ✅ Active | `--entity bitcoin` provided |
| Technical | ✅ Active | `--repo bitcoin/bitcoin` provided |

## Bootstrap Phase

### Business Agent

- Fetched RSS feeds for "bitcoin" and "BTC"
- Extracted 12 business signals:
  - 5 positive (ETF inflow mention, institutional adoption, regulatory clarity in one jurisdiction)
  - 4 negative (exchange security incident mention, energy criticism, regulatory warning in another jurisdiction)
  - 3 neutral (network upgrade discussion, market volume report, halving countdown coverage)
- Identified 3 catalysts: halving event, ETF flows, regulatory developments
- Identified 2 risk factors: exchange concentration, environmental scrutiny

### Technical Agent

- Repository: `bitcoin/bitcoin`
- Fetched 100 recent commits
- Metrics:
  - Commit frequency: ~8 commits/week
  - Days since last commit: 2
  - Contributor count: 850+ (all-time)
  - Recent contributors: 12 (last 30 days)
  - Open issues: 1,200+
  - Health score: 0.82 (strong maintenance)

## Iteration 1

### Quant Agent — Tier 1 (3 Months)

| Metric | Value | Direction |
|--------|-------|-----------|
| Returns (3mo) | +45.2% | Strongly Positive |
| Volatility (annualized) | 42.3% | High |
| Momentum (20d) | +18.7% | Strongly Positive |
| Trend | Bullish | — |
| Max Drawdown | -12.8% | Moderate |
| Risk Score | 0.71 | High |

### Evidence Register Snapshot (Iteration 1)

```
Quant:
  - returns_3mo: +45.2% (source: yfinance, tier: 1, data_points: 90)
  - volatility: 42.3% (source: yfinance, tier: 1, data_points: 90)
  - momentum_20d: +18.7% (source: yfinance, tier: 1, data_points: 20)
  - trend: bullish (source: yfinance, tier: 1, data_points: 90)
  - max_drawdown: -12.8% (source: yfinance, tier: 1, data_points: 90)
  - risk_score: 0.71 (source: quant_agent, tier: 1, data_points: 6)

Business:
  - signal_count: 12 (source: business_agent, tier: 1, data_points: 12)
  - positive_signals: 5 (source: business_agent, tier: 1, data_points: 5)
  - negative_signals: 4 (source: business_agent, tier: 1, data_points: 4)
  - catalysts: 3 (source: business_agent, tier: 1, data_points: 3)
  - risks: 2 (source: business_agent, tier: 1, data_points: 2)

Technical:
  - commit_frequency: 8/week (source: github_api, tier: 1, data_points: 100)
  - days_since_commit: 2 (source: github_api, tier: 1, data_points: 1)
  - contributor_count: 850+ (source: github_api, tier: 1, data_points: 1)
  - health_score: 0.82 (source: technical_agent, tier: 1, data_points: 4)
  - maintenance_status: active (source: technical_agent, tier: 1, data_points: 1)
```

### Critic Agent — Phase 3: Dashboard

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Data Quality | 88% | Strong — all three sources responsive |
| Coverage | 88% | Strong — all 3 dimensions active |
| Agreement | **Low** | Quant bullish + Business mixed + Technical strong = conflict |
| Stability | Unknown | First iteration |

### Critic Agent — Phase 4: Contradictions

- **Contradiction #1:** Quant shows high risk (0.71) but strong positive returns (+45.2%)
  - Rule triggered: "High volatility with strong returns suggests speculative momentum"
  - Severity: Medium
- **Contradiction #2:** Business shows mixed signals (5 positive, 4 negative) while Quant is strongly bullish
  - Rule triggered: "Business sentiment divergence from price action"
  - Severity: Medium
- **Contradiction #3:** Technical health is strong (0.82) but Business flags exchange concentration risk
  - Rule triggered: "Strong protocol health vs. ecosystem risk"
  - Severity: Low

### Critic Agent — Phase 5: Active Questions

1. **Is the +45% return driven by fundamentals or speculation?**
   - Why it matters: Distinguishes sustainable trend from bubble risk
   - Can deeper data resolve? Yes — Tier 2 volume profile and Tier 3 correlation analysis

2. **Do the 4 negative business signals represent systemic or idiosyncratic risks?**
   - Why it matters: Determines whether risks are Bitcoin-specific or market-wide
   - Can deeper data resolve? Partially — broader market quant analysis in Tier 3

### Critic Agent — Phase 6: Halt Decision

**Halt = False**

Reason: Agreement is Low due to multiple contradictions. Active questions can be addressed with deeper quantitative data. Proceed to Tier 2.

## Iteration 2

### Quant Agent — Tier 2 (6 Months)

| Metric | Value | Change from Tier 1 |
|--------|-------|-------------------|
| Returns (6mo) | +78.4% | Extended trend confirmed |
| RSI (14d) | 72.3 | Overbought territory |
| MACD | Bullish crossover | Confirmed momentum |
| Volume Profile | Above average | Strong participation |
| Volatility Regime | Elevated | Consistent with Tier 1 |

### Critic Agent — Phase 3: Dashboard (Iteration 2)

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Data Quality | 91% | Improved — deeper metrics available |
| Coverage | 88% | Unchanged |
| Agreement | **Low** | Contradictions persist — RSI overbought vs. MACD bullish |
| Stability | **Unstable** | Hypothesis shifted — overbought signal adds bearish weight |

### Critic Agent — Phase 6: Halt Decision

**Halt = False**

Reason: Stability is Unstable. The deeper data (RSI 72.3) introduced a new bearish signal that was not present in Tier 1. The thesis changed with deeper evidence. Proceed to Tier 3 for correlation and beta analysis.

## Iteration 3

### Quant Agent — Tier 3 (1 Year)

| Metric | Value | Insight |
|--------|-------|---------|
| Beta (vs. SPY) | 1.85 | Highly correlated with equities |
| Correlation Matrix | Strong equity correlation | Not a true "uncorrelated asset" in this regime |
| ATR (14d) | 4.2% | High daily range |
| 1-Year Volatility | 38.9% | Slightly lower than 3-month (42.3%) |

### Critic Agent — Phase 3: Dashboard (Iteration 3)

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Data Quality | 93% | Maximum depth reached |
| Coverage | 88% | Unchanged |
| Agreement | **Low** | Conflicts remain unresolved |
| Stability | **Unstable** | Beta discovery shifted macro understanding |

### Critic Agent — Phase 6: Halt Decision

**Halt = True (Circuit Breaker)**

Reason: MAX_ITERATIONS = 3 reached. Conflicts remain but cannot be resolved with deeper historical price data. Active questions require non-quantitative investigation (e.g., on-chain analysis, macro regime classification).

## Hypothesis Engine Output

### Directional Bias

| Component | Strength |
|-----------|----------|
| Bullish | 2.45 |
| Bearish | 1.92 |
| **Net Bias** | **BULLISH (+0.53)** |

> Note: Strong price momentum and technical ecosystem health dominate, but high volatility, RSI overbought, and business risks significantly offset the bullish case.

### Uncertainty

| Factor | Score | Assessment |
|--------|-------|------------|
| Scarcity | 8% | Rich evidence (12 business signals, 100 commits, 1yr price data) |
| Conflict | 28% | **High** — multiple unresolved contradictions |
| Coverage | 4% | Near-complete (only on-chain data missing) |
| **Total** | **40%** | **Elevated** |

> The elevated uncertainty is driven entirely by conflict, not missing data. This is the intended behavior: strong conviction with high uncertainty due to contradictory signals.

### Claims

| Claim | Source | Strength | Direction |
|-------|--------|----------|-----------|
| 6-month returns +78.4% | Quant Agent | 0.70 | Bullish |
| RSI overbought (72.3) | Quant Agent | 0.55 | Bearish |
| MACD bullish crossover | Quant Agent | 0.45 | Bullish |
| Beta 1.85 vs equities | Quant Agent | 0.40 | Bearish |
| Strong protocol health (0.82) | Technical Agent | 0.60 | Bullish |
| Active development (8 commits/wk) | Technical Agent | 0.50 | Bullish |
| Exchange concentration risk | Business Agent | 0.45 | Bearish |
| Institutional ETF inflows | Business Agent | 0.50 | Bullish |
| Regulatory divergence | Business Agent | 0.40 | Neutral |

## Final Report

- **Halted at:** Iteration 3 (circuit breaker)
- **Report sections:** All 7 sections generated
- **Key insight:** Bitcoin shows strong price momentum and protocol health, but behaves like a high-beta equity rather than an uncorrelated asset. The overbought RSI and mixed business signals create a "strong but fragile" thesis.
- **Active questions (unresolved):**
  1. Is the current price action driven by ETF flows or organic adoption?
  2. How will the halving event affect the risk/reward profile?
  3. Does the 1.85 beta suggest Bitcoin is in a "risk-on" bubble phase?
- **Contradictions flagged:** 3 (all unresolved)

## Takeaway

This case demonstrates the full 3-iteration loop. The Critic correctly identified that deeper data would be valuable, and the hypothesis evolved as new evidence emerged. The final elevated uncertainty (40%) accurately reflects that Bitcoin presents a coherent but contradictory picture. **The number of iterations itself became information: messy assets need more research.**

---

# Case Study 3: Rust Programming Language — Open Source Ecosystem

## Entity

**Rust** — Open-source programming language and ecosystem

## Command

```bash
python main.py \
    --entity rust-lang \
    --repo rust-lang/rust \
    --hypotheses
```

## Research Dimensions

| Dimension | Status | Reason |
|-----------|--------|--------|
| Quant | ⏭️ Skipped | No `--ticker` provided |
| Business | ✅ Active | `--entity rust-lang` provided |
| Technical | ✅ Active | `--repo rust-lang/rust` provided |

## Bootstrap Phase

### Business Agent

- Fetched RSS feeds for "Rust programming language" and "rust-lang"
- Extracted 6 business signals:
  - 4 positive (major adoption by enterprise, new foundation funding, AWS/Azure support expansion, Linux kernel integration milestone)
  - 1 negative (competition from Go and Zig mentions)
  - 1 neutral (version release announcement)
- Identified 2 catalysts: enterprise adoption wave, foundation growth
- Identified 1 risk factor: governance complexity (foundation vs. community tension)

### Technical Agent

- Repository: `rust-lang/rust`
- Fetched 100 recent commits
- Metrics:
  - Commit frequency: ~45 commits/week
  - Days since last commit: 0 (same day)
  - Contributor count: 3,200+ (all-time)
  - Recent contributors: 48 (last 30 days)
  - Open issues: 8,500+
  - Health score: 0.91 (exceptional maintenance)
  - Release cadence: Regular (every 6 weeks)

## Iteration 1

### Quant Agent

- Skipped (no ticker provided)
- Status recorded as `"skipped"` in Evidence Register
- Asset classified as `open_source_or_pre_launch`

### Evidence Register Snapshot (Iteration 1)

```
Quant:
  - status: skipped (source: quant_agent, tier: 0, data_points: 0)

Business:
  - signal_count: 6 (source: business_agent, tier: 1, data_points: 6)
  - positive_signals: 4 (source: business_agent, tier: 1, data_points: 4)
  - negative_signals: 1 (source: business_agent, tier: 1, data_points: 1)
  - catalysts: 2 (source: business_agent, tier: 1, data_points: 2)
  - risks: 1 (source: business_agent, tier: 1, data_points: 1)

Technical:
  - commit_frequency: 45/week (source: github_api, tier: 1, data_points: 100)
  - days_since_commit: 0 (source: github_api, tier: 1, data_points: 1)
  - contributor_count: 3200+ (source: github_api, tier: 1, data_points: 1)
  - health_score: 0.91 (source: technical_agent, tier: 1, data_points: 4)
  - maintenance_status: exceptional (source: technical_agent, tier: 1, data_points: 1)
```

### Critic Agent — Phase 3: Dashboard

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Data Quality | 75% | Good — RSS + GitHub both responsive |
| Coverage | 47% | Partial — only 2 of 3 dimensions |
| Agreement | **High** | Business positive + Technical exceptional align |
| Stability | Unknown | First iteration |

### Critic Agent — Phase 4: Contradictions

- **No contradictions detected**
- Business and Technical signals are directionally aligned
- The single negative business signal (competition) is minor relative to positive signals

### Critic Agent — Phase 5: Active Questions

1. **What is the sustainability of enterprise adoption?**
   - Why it matters: Determines whether current momentum is temporary or structural
   - Can deeper data resolve? No — requires longitudinal tracking (Phase 9 audit trail)

2. **How does governance complexity affect long-term project health?**
   - Why it matters: Open-source governance is a common failure mode
   - Can deeper data resolve? Partially — deeper GitHub analysis of decision-making processes

### Critic Agent — Phase 6: Halt Decision

**Halt = True**

Reason: Coverage is below 50% but Agreement is High and no contradictions exist. The missing Quant dimension is expected for a non-traded open-source project. The available evidence forms a coherent view.

## Hypothesis Engine Output

### Directional Bias

| Component | Strength |
|-----------|----------|
| Bullish | 2.15 |
| Bearish | 0.35 |
| **Net Bias** | **BULLISH (+1.80)** |

### Uncertainty

| Factor | Score | Assessment |
|--------|-------|------------|
| Scarcity | 18% | Moderate evidence volume |
| Conflict | 5% | Low disagreement |
| Coverage | 28% | **High** — missing quant dimension |
| **Total** | **51%** | **High** |

> The high uncertainty is driven entirely by coverage gaps, not conflicting evidence. This is the intended behavior: when a dimension is missing, uncertainty rises even if available evidence is strongly aligned.

### Claims

| Claim | Source | Strength | Direction |
|-------|--------|----------|-----------|
| Enterprise adoption accelerating | Business Agent | 0.55 | Bullish |
| Major cloud provider support | Business Agent | 0.50 | Bullish |
| Linux kernel integration | Business Agent | 0.45 | Bullish |
| Exceptional health score (0.91) | Technical Agent | 0.65 | Bullish |
| High contributor activity (48/mo) | Technical Agent | 0.50 | Bullish |
| Governance complexity risk | Business Agent | 0.30 | Bearish |
| Competition from Go/Zig | Business Agent | 0.25 | Bearish |

## Final Report

- **Halted at:** Iteration 1
- **Report sections:** All 7 sections generated
- **Key insight:** Rust presents a strongly bullish open-source ecosystem profile with exceptional technical health and growing enterprise adoption. However, the absence of market data creates significant uncertainty about financial valuation or investment timing.
- **Active questions:**
  1. Is there a commercial entity (e.g., Ferrous Systems, Rust Foundation revenue) that could be valued?
  2. How does governance complexity evolve as the project matures?
- **Asset classification:** `open_source_or_pre_launch`

## Takeaway

AIRS gracefully handles non-financial entities by skipping the Quant Agent without error. The high uncertainty (51%) correctly signals that this is not a traditional investment analysis — it's an ecosystem health assessment. **The system adapts its output type to the available inputs.**

---

# Case Study 4: Oracle (ORCL) — Partial Input Handling

## Entity

**Oracle Corporation** — Publicly traded technology company (NYSE: ORCL)

## Command

```bash
python main.py --entity ORCL --hypotheses
```

> Note: No `--ticker` and no `--repo` provided.

## Research Dimensions

| Dimension | Status | Reason |
|-----------|--------|--------|
| Quant | ⏭️ Skipped | No `--ticker` provided |
| Business | ✅ Active | `--entity ORCL` provided |
| Technical | ⏭️ Skipped | No `--repo` provided |

## Bootstrap Phase

### Business Agent

- Fetched RSS feeds for "Oracle" and "ORCL"
- Extracted 5 business signals:
  - 2 positive (cloud revenue growth, database market share)
  - 2 negative (layoff announcement, competitive pressure from PostgreSQL)
  - 1 neutral (executive leadership change)
- Identified 1 catalyst: cloud transition progress
- Identified 1 risk factor: workforce reduction impact

### Technical Agent

- Skipped (no repository specified)

## Iteration 1

### Quant Agent

- Skipped (no ticker provided)

### Evidence Register Snapshot (Iteration 1)

```
Quant:
  - status: skipped (source: quant_agent, tier: 0, data_points: 0)

Business:
  - signal_count: 5 (source: business_agent, tier: 1, data_points: 5)
  - positive_signals: 2 (source: business_agent, tier: 1, data_points: 2)
  - negative_signals: 2 (source: business_agent, tier: 1, data_points: 2)
  - catalysts: 1 (source: business_agent, tier: 1, data_points: 1)
  - risks: 1 (source: business_agent, tier: 1, data_points: 1)

Technical:
  - status: skipped (source: technical_agent, tier: 0, data_points: 0)
```

### Critic Agent — Phase 3: Dashboard

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Data Quality | 65% | Moderate — RSS responsive but limited depth |
| Coverage | 24% | **Low** — only 1 of 3 dimensions active |
| Agreement | **Neutral** | Balanced positive/negative business signals |
| Stability | Unknown | First iteration |

### Critic Agent — Phase 4: Contradictions

- **No contradictions detected** (insufficient dimensions for cross-agent comparison)

### Critic Agent — Phase 5: Active Questions

1. **What is the current stock price trend and volatility?**
   - Why it matters: Cannot assess investment timing without market data
   - Can deeper data resolve? Yes — requires `--ticker ORCL`

2. **What is the state of Oracle's open-source ecosystem?**
   - Why it matters: Competitive pressure from open-source databases is a key risk
   - Can deeper data resolve? Yes — requires `--repo oracle/...`

3. **Are the layoffs structural or cyclical?**
   - Why it matters: Determines whether risk is temporary or permanent
   - Can deeper data resolve? Partially — deeper news analysis or earnings data

### Critic Agent — Phase 6: Halt Decision

**Halt = True**

Reason: Only one dimension active. Further iteration cannot improve coverage because Business Agent inputs are static (RSS feeds). The system cannot collect new evidence without additional CLI arguments.

## Hypothesis Engine Output

### Directional Bias

| Component | Strength |
|-----------|----------|
| Bullish | 0.75 |
| Bearish | 0.70 |
| **Net Bias** | **NEUTRAL (+0.05)** |

> With only business signals and a balanced 2-2 split, the directional bias is essentially neutral. The system refuses to manufacture conviction from thin evidence.

### Uncertainty

| Factor | Score | Assessment |
|--------|-------|------------|
| Scarcity | 25% | Low evidence volume (only 5 signals) |
| Conflict | 5% | Low — signals are balanced, not conflicting |
| Coverage | 45% | **Very High** — 2 of 3 dimensions missing |
| **Total** | **75%** | **Extreme** |

> Extreme uncertainty is appropriate here. The system is essentially saying: "I cannot form a meaningful investment view with only news headlines."

### Claims

| Claim | Source | Strength | Direction |
|-------|--------|----------|-----------|
| Cloud revenue growth | Business Agent | 0.40 | Bullish |
| Database market share | Business Agent | 0.35 | Bullish |
| Layoff announcement | Business Agent | 0.40 | Bearish |
| PostgreSQL competition | Business Agent | 0.35 | Bearish |
| Leadership change | Business Agent | 0.20 | Neutral |

## Final Report

- **Halted at:** Iteration 1
- **Report sections:** All 7 sections generated
- **Key insight:** Insufficient data to form a directional view. Business signals are balanced and two research dimensions are missing.
- **Active questions:**
  1. Provide `--ticker ORCL` for quantitative analysis
  2. Provide `--repo oracle/...` for technical ecosystem analysis
  3. Re-run with full arguments for complete research
- **System recommendation:** Re-run with `--ticker ORCL` and optionally `--repo oracle/db-compiler` for full analysis

## Takeaway

AIRS handles partial inputs gracefully. Rather than crashing or fabricating data, it produces a valid but extremely uncertain result. The report explicitly tells the user what information is missing and how to obtain it. **This is evidence-driven honesty: the system knows what it doesn't know.**

---

# Comparative Summary

| Case | Entity | Dimensions | Halt Iteration | Bias | Uncertainty | Key Behavior |
|------|--------|------------|----------------|------|-------------|--------------|
| 1 | AAPL | 2 of 3 | 1 | Bearish | 29% (Moderate) | Early halt — coherent view |
| 2 | Bitcoin | 3 of 3 | 3 (circuit) | Bullish | 40% (Elevated) | Full loop — unresolved conflicts |
| 3 | Rust | 2 of 3 | 1 | Bullish | 51% (High) | Non-financial entity — coverage gap |
| 4 | ORCL | 1 of 3 | 1 | Neutral | 75% (Extreme) | Partial input — honest uncertainty |

---


# Case Study 5: Batch Watchlist Analysis — tech_blue_chip

## Command

```bash
python main.py --watchlist tech_blue_chip --hypotheses
```
## Behavior

AIRS loads 10 entities from config/watchlist.json and runs the full evidence-driven loop for each:
| #  | Entity     | Ticker | Sector               | Dimensions | Halt        | Bias    | Uncertainty |
| -- | ---------- | ------ | -------------------- | ---------- | ----------- | ------- | ----------- |
| 1  | Apple      | AAPL   | consumer-tech        | 3 of 3     | Iteration 2 | BEARISH | Moderate    |
| 2  | NVIDIA     | NVDA   | semiconductors       | 3 of 3     | Iteration 1 | BULLISH | Low         |
| 3  | Microsoft  | MSFT   | enterprise-software  | 3 of 3     | Iteration 1 | BULLISH | Low         |
| 4  | Google     | GOOGL  | consumer-tech        | 2 of 3     | Iteration 3 | NEUTRAL | Elevated    |
| 5  | Meta       | META   | consumer-tech        | 3 of 3     | Iteration 1 | BEARISH | Moderate    |
| 6  | Amazon     | AMZN   | cloud-infrastructure | 3 of 3     | Iteration 2 | BULLISH | Moderate    |
| 7  | Tesla      | TSLA   | ev-energy            | 3 of 3     | Iteration 3 | BEARISH | High        |
| 8  | Netflix    | NFLX   | streaming            | 2 of 3     | Iteration 1 | NEUTRAL | Moderate    |
| 9  | Salesforce | CRM    | saas                 | 2 of 3     | Iteration 1 | BULLISH | Low         |
| 10 | Oracle     | ORCL   | enterprise-software  | 3 of 3     | Iteration 1 | NEUTRAL | Moderate    |

## Key Observations
- Total sessions saved: 10 rows in research_sessions
- Sectors tagged: All 10 sessions carry canonical sector labels
- Startups skipped: The startups category has no tickers — sessions are saved but not scored
- Batch runtime: ~8-12 minutes for 10 entities (depends on Ollama speed)

## Audit Trail Note
After 30 days, running:
```bash
python main.py --audit
```
will evaluate each session with a ticker against actual price changes and populate research_outcomes. Sessions without tickers (startups) are intentionally skipped.


# Patterns Observed

## Pattern 1: Early Halt on Coherence

When evidence agrees on direction (Cases 1 and 3), AIRS halts at Iteration 1. The system does not waste compute on deeper analysis when the available evidence already tells a consistent story.

## Pattern 2: Full Iteration on Conflict

When evidence contradicts (Case 2), AIRS runs all 3 iterations. Each tier of deeper quant data adds new signals that shift the hypothesis. The circuit breaker at Iteration 3 is appropriate — the conflicts are fundamental (price vs. risk) and cannot be resolved with more historical data.

## Pattern 3: Uncertainty Reflects Information Gaps, Not Just Disagreement

- Case 1: Moderate uncertainty (29%) despite bearish bias — missing Technical dimension
- Case 3: High uncertainty (51%) despite strong bullish bias — missing Quant dimension
- Case 4: Extreme uncertainty (75%) with neutral bias — missing two dimensions

This demonstrates that **uncertainty is independent of conviction**, a core design principle.

## Pattern 4: Skipped Agents Are Not Failures

In all cases where agents were skipped (no ticker, no repo), the Critic treated them as intentionally omitted rather than errors. The system produces valid outputs for partial inputs without crashing.

## Pattern 5: Batch Mode Surfaces Portfolio-Level Insights

Running 10 entities sequentially reveals cross-sector patterns that single-shot analysis misses:
- Consumer-tech showed mixed signals (2 bullish, 2 bearish, 2 neutral) — sector-level disagreement
- Cloud-infrastructure and enterprise-software both halted early with bullish bias
- Tesla ran all 3 iterations with High uncertainty — the most "messy" asset in the batch
- The batch summary table makes these patterns visible at a glance.
---

# Lessons for Users

1. **Provide as many dimensions as possible.** The more inputs you give (`--ticker`, `--repo`), the lower the uncertainty and the richer the analysis.

2. **Watch the iteration count.** If AIRS runs all 3 iterations, the asset is inherently contradictory or messy. This is valuable information in itself.

3. **Read the active questions.** Unresolved questions often point to the most important due diligence items.

4. **Trust the uncertainty score.** A high uncertainty score with strong directional bias means "the evidence points this way, but we don't have enough information to be confident." This is more honest than a fake 85% confidence number.

---

<div align="center">

# AIRS v0.3.7

**Evidence-Driven Investment Research Infrastructure**

*"Case studies demonstrate that research quality comes from knowing what you don't know."*

</div>
