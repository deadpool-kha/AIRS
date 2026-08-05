# AIRS Limitations

&gt; **Version:** 0.3.7  
&gt; **Last Updated:** 2026-08-05

---

## Why This Document Exists

AIRS is designed to be **honest about what it does not know.**

Most AI systems hide their limitations behind confident-sounding outputs. AIRS does the opposite. Every limitation listed here is a known boundary. Documenting them prevents misuse, manages expectations, and identifies exactly where the system can improve.

---

## 1. Data Layer Limitations

### Public Data Only
AIRS relies entirely on publicly available information. It cannot access:
- Proprietary analyst reports
- Paid financial databases (Bloomberg, Refinitiv, Capital IQ)
- Private company financials
- Insider transaction data
- Real-time order book or Level 2 market data

### Historical Gaps
- **Market data:** Retrieved via `yfinance`, which is unofficial and may break due to external API changes.
- **News data:** RSS feeds provide **live articles only.** There is no access to historical news archives. Running the same analysis tomorrow may yield different business signals because the news feed has changed.
- **GitHub data:** Only the most recent 100 commits and current repository state are evaluated. Historical contributor trends, release cycles over time, or code churn evolution are not tracked.

---

## 2. Quantitative Analysis Limitations

### Closing Prices Only
All quantitative metrics are computed from **daily closing prices.** The system does not account for:
- Intraday price movements
- Opening gaps
- High/low volatility within a session
- After-hours or pre-market trading

### Tiered Depth, Not Breadth
The Quant Agent deepens analysis by extending the lookback period (3mo → 6mo → 1yr), but it does not broaden analysis by adding new data types. For example:
- No options market data (implied volatility, open interest)
- No fundamental data (P/E, revenue, earnings, balance sheet)
- No macroeconomic indicators (interest rates, inflation, GDP)
- No on-chain data for crypto assets

### Heuristic Thresholds
Signal strength thresholds (e.g., RSI &gt; 75 = overbought, drawdown &gt; 20% = severe) are **intuitive heuristics, not statistically validated cutoffs.** They have not been backtested against historical market regimes.

---

## 3. Business Agent Limitations

### Live RSS Only
The Business Agent reads current RSS feeds. It cannot:
- Retrieve news from a specific historical date
- Access paywalled articles
- Distinguish between high-quality journalism and low-quality content farms
- Weight sources by credibility (all RSS sources are treated equally)

### Static Inputs Across Iterations
Because RSS is a live feed, re-running the Business Agent in Iteration 2 or 3 typically produces the same results as Iteration 1. The loop cannot "dig deeper" into business news by iterating.

### LLM Hallucination Boundaries
The Business Agent uses Ollama (`qwen2.5:7b`) for summarization and signal extraction. While prompts are constrained to existing evidence, small local LLMs can still:
- Misinterpret ambiguous headlines
- Overweight recent news relative to older context
- Invent connections between unrelated events

---

## 4. Technical Agent Limitations

### Single Snapshot
The Technical Agent evaluates one GitHub repository at a single point in time. It does not:
- Track repository evolution over months or years
- Analyze code quality, test coverage, or security posture
- Evaluate related repositories or the broader ecosystem
- Distinguish between core contributors and drive-by commits

### Rate Limiting
Unauthenticated GitHub API calls are limited to **60 requests per hour.** For large analyses or frequent runs, this may cause delays or incomplete data.

---

## 5. Risk Agent Limitations

### Legacy Bridge
The Risk Agent still reads from a legacy `agent_outputs` dictionary rather than reading directly from the Evidence Register. This creates a minor architectural inconsistency and means some Evidence Register metadata (tier, data period) is not visible to the Risk Agent.

### Rule-Based Severity
Risk severity classification (HIGH / MEDIUM / LOW) uses hardcoded thresholds. It does not adapt to asset class (a 20% drawdown means something different for Bitcoin than for a Treasury bond).

---

## 6. Hypothesis Engine Limitations

### Not Calibrated to History
Directional strength scores and uncertainty factors are **heuristic formulas.** They have not been validated against historical outcomes. The system cannot yet answer:
- "How often does a BEARISH bias with Low uncertainty actually precede a price decline?"
- "What is the base rate of contradiction resolution across iterations?"

### No Probability Claims
AIRS deliberately avoids probability statements. This is a design choice, not a technical limitation, but users should understand that AIRS does not output:
- "70% chance of decline"
- Expected return estimates
- Confidence intervals

Instead, it outputs **evidence-weighted directional bias** and **epistemic uncertainty** as separate dimensions.

---

## 7. Research Process Limitations

### Iteration Asymmetry
Only the **Quant Agent** receives updated inputs between iterations. Business and Technical agents operate on static data. This means:
- Iteration 2 and 3 primarily add quantitative depth
- They do not add new business catalysts or technical ecosystem changes

### Halt Logic Edge Cases
The Critic Agent halts when evidence is coherent or when the circuit breaker (3 iterations) is reached. However:
- `max_iterations` halt does not mean the thesis is *correct* — it means the system exhausted its available evidence
- Some assets may appear "coherent" at Iteration 1 simply because too few dimensions are active, not because the evidence is strong

---

## 8. Report Generator Limitations

### PDF Export Dependencies
PDF generation requires `weasyprint` and `markdown` Python packages, plus **GTK+ system libraries on Windows.** If these are missing, PDF export fails gracefully and only Markdown is produced.

### Template Rigidity
The Jinja2 template (`report.md.j2`) produces a fixed 7-section structure. It does not yet support:
- Custom report sections
- User-defined formatting
- Multi-asset comparison reports
- Interactive charts or visualizations

---

## 9. Scope Boundaries (What AIRS Explicitly Does NOT Do)

| Capability | Status | Reason |
|------------|--------|--------|
| Predict future prices | ❌ Not designed to | AIRS structures research, it does not forecast |
| Execute trades | ❌ Out of scope | No brokerage integration |
| Manage portfolios | ❌ Out of scope | No position sizing or allocation logic |
| Real-time monitoring | ❌ Not implemented | Runs on-demand, not as a daemon |
| Sentiment analysis from social media | ❌ Not implemented | No Twitter/X, Reddit, or Discord integration |
| ESG scoring | ❌ Not implemented | No environmental/social/governance data |
| Macro analysis | ❌ Not implemented | No Fed policy, inflation, or geopolitical modeling |
| On-chain analysis | ❌ Not implemented | No blockchain node or Dune Analytics integration |
| Fundamental valuation | ❌ Not implemented | No DCF, comparables, or earnings modeling |

---

## 10. Hardware & Environment Limitations

### Consumer Hardware Target
AIRS is optimized for:
- NVIDIA GTX 1060 6GB
- 16 GB RAM
- Windows 10 / Linux / macOS

Ollama inference on weaker hardware may cause timeouts. The Business Agent may skip if Ollama is unavailable.

### No Cloud Deployment
AIRS is local-first. There is currently no:
- Docker container
- Cloud deployment guide
- Multi-user support
- API server mode

---

## Known Issues (Active)

| Issue | Impact | Planned Resolution |
|-------|--------|-------------------|
| Report footer shows `v0.3.6` instead of `v0.3.7` | Cosmetic | Patch in `reports/templates/report.md.j2` |
| `research_sessions` and `research_outcomes` tables not yet created | Cannot persist session history | Phase 9 — Audit Trail |
| `--audit` CLI flag not yet implemented | Cannot query historical accuracy | Phase 9 — Audit Trail |
| Risk Agent legacy bridge | Minor architectural debt | Phase 9 — Direct Evidence Register integration |

---

## How to Interpret These Limitations

AIRS is a **research infrastructure**, not an oracle.

Every limitation above represents a boundary where human judgment must take over. The system is designed to:
1. Collect and structure evidence up to its boundary
2. Clearly signal where the boundary is
3. Hand off to the user for everything beyond it

If AIRS cannot access historical news, it tells you.  
If AIRS halted at iteration 1 due to missing dimensions, it tells you.  
If AIRS has never backtested its thresholds, it tells you.

**Transparency about limitations is a feature, not a bug.**

---

&lt;div align="center"&gt;

## AIRS v0.3.7

**Evidence-Driven Investment Research Infrastructure**

*"Knowing the boundaries of your knowledge is the beginning of wisdom."*

&lt;/div&gt;