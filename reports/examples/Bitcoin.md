# Investment Research Memo: Bitcoin

**Asset Type:** `public_stock_with_repo`  
**Ticker:** BTC-USD  
**Generated:** 2026-08-14 06:48 UTC  
**Research Iterations:** 3  
**Halt Reason:** Circuit breaker: maximum iterations reached

---

## 1. Executive Summary

**Directional Bias: BEARISH** — The evidence supports a cautious or negative investment thesis.

**Uncertainty Level:** 10% — **Low**  
*Scarcity=0.00, Conflict=0.10, Coverage=0.00*

The research loop halted after **3 iterations** because: *Circuit breaker: maximum iterations reached*.


---

## 2. Audit Dashboard

| Dimension | Score | Details |
|-----------|-------|---------|
| Data Quality | 82% | quant, business, technical |
| Coverage | 100% | 18/18 features present |
| Agreement | Low | 1 positive, 2 negative, 1 neutral across 4 dimensions |
| Stability | Stable | No dimension flipped direction |

---

## 3. Investment Thesis

### 3.1 Directional Bias

- **Bullish Strength:** 0.86 (2 claims)
- **Bearish Strength:** 3.58 (7 claims)
- **Net Score:** -2.72
- **Overall Direction:** BEARISH

### 3.2 Bull Case

**Thesis:** Bitcoin is undervalued with upside potential

| Evidence | Source | Strength | Raw Value |
|----------|--------|----------|-----------|
| 2 catalyst(s) identified | business | 0.41 | 2 |
| High development activity: 100.0/week | technical | 0.45 | 100.0 |

**Total Strength:** 0.86

### 3.3 Bear Case

**Thesis:** Bitcoin is overvalued or faces significant risks

| Evidence | Source | Strength | Raw Value |
|----------|--------|----------|-----------|
| Price in downtrend | quant | 0.60 | downtrend |
| MACD bearish — negative momentum | quant | 0.50 | bearish |
| High beta (1.56) — elevated systematic risk | quant | 0.45 | 1.5553 |
| High risk score: 0.67 | quant | 0.75 | 0.67 |
| Severe drawdown: 53.1% | quant | 0.70 | 0.5306 |
| 1 negative business signal(s) | business | 0.25 | 1 |
| 1 business risks identified | business | 0.33 | 1 |

**Total Strength:** 3.58

### 3.4 Base / Neutral Case

**Thesis:** Bitcoin is fairly valued with moderate growth

| Evidence | Source | Strength | Raw Value |
|----------|--------|----------|-----------|
| Normal volatility regime | quant | 0.25 | normal |
| Moderate ecosystem health (health: 0.70) | technical | 0.30 | 0.7 |

**Total Strength:** 0.55


### 3.5 Uncertainty Analysis

**Uncertainty Score:** 10% — **Low**

| Factor | Value | Interpretation |
|--------|-------|----------------|
| Scarcity | 0.00 | Few signals available |
| Conflict | 0.10 | Dimensions disagree |
| Coverage | 0.00 | Missing research dimensions |

*Scarcity=0.00, Conflict=0.10, Coverage=0.00*

---


---

## 4. Evidence Register Summary

### 4.1 Evidence by Source

| Source | Items |
|--------|-------|
| Business | 1 item: `business_context` |
| Technical | 1 item: `technical_context` |
| Quant | 17 items: `price_data`, `returns`, `volatility`, `momentum`, `moving_averages`, `drawdown`, `risk_score`, `trend`, `current_price`, `data_points`, `rsi`, `macd`, `volume_profile`, `atr`, `volatility_regime`, `beta`, `correlation_matrix` |

### 4.2 Evidence by Tier

| Tier | Items |
|------|-------|
| Tier 1 | 9 items: `returns`, `volatility`, `momentum`, `moving_averages`, `drawdown`, `risk_score`, `trend`, `current_price`, `data_points` |
| Tier 2 | 3 items: `rsi`, `macd`, `volume_profile` |
| Tier 3 | 5 items: `price_data`, `atr`, `volatility_regime`, `beta`, `correlation_matrix` |

### 4.3 Quantitative Evidence

| Metric | Value |
|--------|-------|
| Returns | daily_mean: -0.1323, daily_std: 2.2677, weekly: 2.1400, monthly: -0.8500 |
| Volatility | 0.3600 |
| Momentum | 5d: 0.0214, 10d: -0.0181, 20d: 0.0058, 30d: 0.0026 |
| Moving Averages | sma_10: 63825.0000, sma_20: 64335.8600, sma_50: 63263.6300 |
| Drawdown | max_drawdown: 0.5306, peak_date: 2025-10-06, trough_date: 2026-06-30 |
| Risk Score | 0.6700 |
| Trend | downtrend |
| Current Price | 64159.9900 |
| Rsi | 37.8700 |
| Macd | macd_line: -84.0891, signal_line: 44.5275, histogram: -128.6166, signal: bearish |
| Volume Profile | avg_volume: 46445121459.0000, volume_trend: decreasing, relative_volume: 0.5100 |
| Atr | 1479.0474 |
| Volatility Regime | normal |
| Beta | 1.5553 |
| Correlation Matrix | SPY: 0.4881, QQQ: 0.4454 |

### 4.4 Business Evidence


**Summary:** In recent developments, Metaplanet has denied selling $320 million in Bitcoin and is launching BitBonds, indicating potential strategic moves in the crypto market. While various news sources are track...
**Signals:**
| Type | Category | Description |
|------|----------|-------------|
| NEUTRAL | Product | Metaplanet is launching BitBonds, which could be a strategic move in the crypto market. |
| NEGATIVE | Market | Bitcoin price is under pressure and facing some bumps on its path to $100,000. |

**Catalysts (2):**
- US PPI and inflation data release
- Fed rate decision

**Risks (1):**
- denial of selling a large amount of Bitcoin by Metaplanet could indicate internal issues or market concerns.


### 4.5 Technical Evidence


| Metric | Value |
|--------|-------|
| Health Score | 0.7 |
| Commit Frequency | 100.0/week |
| Contributors | 30 |
| Open Issues | 691 |
| Days Since Commit | 0 |
| Total Commits | 100 |


### 4.6 Total Evidence Items

**19** evidence items collected across all dimensions.

---

## 5. Risk Assessment

**Overall Risk Level:** HIGH  
**Risks Identified:** 5  
**Warnings:** 0  
**High Severity:** 4

### Identified Risks

| Severity | Category | Description | Source |
|----------|----------|-------------|--------|
| HIGH | Volatility | High risk score: 0.67 | quant_agent |
| HIGH | Drawdown | Significant drawdown: 53.1% | quant_agent |
| HIGH | Momentum | Negative price trend: downtrend | quant_agent |
| HIGH | Market | Bitcoin price is under pressure and facing some bumps on its path to $100,000. | business_agent |
| MEDIUM | Business | denial of selling a large amount of Bitcoin by Metaplanet could indicate internal issues or market concerns. | business_agent |


---

## 6. Active Questions & Unresolved Contradictions

### 6.1 Active Research Questions

*No active questions remain. The Critic found sufficient evidence to form a view.*

### 6.2 Unresolved Contradictions

*No unresolved contradictions. All detected contradictions were either resolved or flagged for human review.*

---

## 7. Appendix

### 7.1 Methodology

This report was generated by the **Autonomous Investment Research System (AIRS)**, an evidence-driven research infrastructure. The system operates through the following pipeline:

1. **Capability Probe** — Detects available research dimensions (quantitative, technical, business)
2. **Bootstrap** — Runs Business and Technical agents once to establish baseline context
3. **Iterative Evidence Accumulation** — Quant Agent runs tiered computations (Tier 1: 3mo → Tier 2: 6mo → Tier 3: 1y)
4. **Critic Audit** — 6-phase rule-based evaluation: Inventory → Signals → Dashboard → Contradictions → Active Questions → Halt Decision
5. **Hypothesis Generation** — Directional Bias + Uncertainty computed from evidence weights
6. **Risk Assessment** — Downside analysis and cross-agent contradiction detection
7. **Report Generation** — Structured memo synthesis

### 7.2 Key Design Principles

- **No fake probabilities.** Directional bias uses raw evidence strength, not normalized percentages.
- **Explicit uncertainty.** Uncertainty is computed independently from directional conviction.
- **Evidence provenance.** Every claim traces back to its source agent, computation tier, and data period.
- **Deterministic analysis.** Financial calculations are rule-based; LLMs are used only for qualitative tasks (news summarization, report prose).
- **Contradiction-first.** The system actively searches for conflicting signals rather than suppressing them.

### 7.3 Limitations

- Research is based on publicly available data only
- Business Agent uses live RSS feeds; historical news access is limited
- Technical Agent analyzes a single repository snapshot
- Quant metrics are computed from closing prices and do not account for intraday movements
- The system does not predict prices; it structures and audits research quality

### 7.4 Disclaimer

*This report is generated for research and educational purposes only. It does not constitute investment advice, an offer to buy or sell securities, or a recommendation of any investment strategy. Always conduct independent due diligence and consult a qualified financial advisor before making investment decisions.*

---

*Report generated by AIRS v0.3.8 — Evidence-Driven Loop Evolution*