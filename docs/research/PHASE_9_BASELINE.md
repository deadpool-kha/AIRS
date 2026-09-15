# Phase 9 Baseline — First Audit Results

> **Audit date:** 2026-09-14

> **Version audited:** v0.3.8 (pre-Phase-9.5 fixes)

> **Purpose:** Reference point for all future audit comparisons

> **Status:** Superseded by any audit run after 2026-09-14


---

## Why This Document Exists

Phase 9 built the infrastructure to measure AIRS's own research accuracy
against real market outcomes. On 2026-09-14, that infrastructure was run
for the first time against a full watchlist of 30 entities.

This document records the results of that first audit — unfiltered. It
is the reference point against which every future audit will be
compared. When Phase 9.5 fixes are validated, the improvement (or
degradation) will be measured against these numbers.

It also records the bugs the audit surfaced. A baseline that hides its
own weaknesses is not a baseline — it is a press release.

---

## Scope

| Field | Value |
|-------|-------|
| Sessions analyzed | 30 (ids 7–36) |
| Sessions scored | 23 (public stocks + crypto) |
| Sessions skipped | 7 (startups without tickers) |
| Sessions deleted pre-audit | 6 (duplicate AAPL/crypto test sessions, ids 1–6) |
| Session date | 2026-08-14 (all sessions) |
| Audit date | 2026-09-14 (day 31) |
| Horizon | 30 calendar days |
| Scoring | Graded, -1.0 to +1.0 (see `data/audit.py`) |

**Note on skipped sessions:** Startups (`Anthropic`, `OpenAI`,
`LangChain`, `Supabase`, `Vercel`, `Mistral AI`, `Replicate`) have no
ticker and cannot be scored against price. They were analyzed and saved
to `research_sessions` but intentionally excluded from outcome scoring.
This matches design decision 1.8.

---

## Headline Result

| Metric | Value |
|--------|-------|
| Overall average score | **-0.0945** |
| Sessions scored | 23 |
| Sessions correct (score > 0) | 11 |
| Sessions wrong (score < 0) | 12 |
| Neutral-correct (score = 1.0) | 4 |

An average score of -0.09 on a scale of -1.0 to +1.0 is functionally a
coin flip with a slight negative edge. This is not surprising for a
first audit. It is also not a passing grade. The value of the number
is not whether it is positive — it is that it now exists and can be
improved.

---

## Breakdown by Uncertainty Level

This is the most consequential finding in the audit.

| Uncertainty Level | Sessions | Avg Score |
|-------------------|----------|-----------|
| Low               | 7        | **-0.4431** |
| Moderate          | 15       | **+0.0815** |
| Elevated          | 1        | -0.2961 |
| High              | 0        | — |
| Extreme           | 0        | — |

**The relationship is inverted.** AIRS's own uncertainty metric is
supposed to signal epistemic humility: "Low uncertainty means we are
confident; High uncertainty means we are not." If that signal were
calibrated, Low-uncertainty sessions should score better than
Moderate-uncertainty sessions.

They score 0.52 points worse.

**Interpretation:** The uncertainty score is currently measuring
*internal evidence coherence*, not *predictive reliability*. When all
dimensions agree, uncertainty drops — but agreement is not the same as
being right. This is a classic overconfidence pattern: the system is
most sure precisely when it has stopped questioning itself.

**Root cause hypothesis:** The magnitude/direction bug (see next
section). Evidence that is directionally unrelated (e.g., beta,
volatility, drawdown) was being counted as if it corroborated the
directional thesis. More "agreeing" signals → lower uncertainty → false
confidence.

**Action:** Fixing the magnitude/direction separation is Priority 1 for
Phase 9.5. Re-run `--audit --force` after that fix. If the inversion
persists, the uncertainty formula itself needs recalibration.

---

## Breakdown by Evidence Strength

| Bucket      | Sessions | Avg Score |
|-------------|----------|-----------|
| Speculative | 0        | — |
| Tentative   | 0        | — |
| Convicted   | 23       | -0.0945 |

**All 23 scored sessions landed in a single bucket.** The thresholds
in `data/audit.py` (`Speculative < 0.5`, `Tentative 0.5–1.5`,
`Convicted > 1.5`) are miscalibrated against the actual distribution
of `bull_strength + bear_strength` in real sessions.

This makes the "evidence strength" grouping currently useless. It cannot
discriminate between sessions that should be trusted and sessions that
should not.

**Action:** Query the actual distribution, recalibrate thresholds, or
replace the metric with a composite (conviction + diversity + depth) as
originally planned for Phase 9.5.

---

## Breakdown by Sector

| Sector                | Sessions | Avg Score |
|-----------------------|----------|-----------|
| cybersecurity         | 1        | **+1.0000** |
| e-commerce            | 1        | **+1.0000** |
| saas                  | 1        | **+1.0000** |
| mobility              | 1        | +0.8743 |
| cloud-infrastructure  | 3        | +0.6086 |
| data-analytics        | 2        | +0.5420 |
| streaming             | 2        | +0.2756 |
| enterprise-software   | 2        | -0.1594 |
| consumer-tech         | 4        | -0.8037 |
| ev-energy             | 1        | -0.9758 |
| semiconductors        | 1        | -1.0000 |
| database              | 1        | -1.0000 |
| l1-blockchain         | 3        | -1.0000 |

**Two distinct patterns emerge:**

**1. Sector-specific behavior is real.** Seven of thirteen sectors
scored +0.5 or better. Cybersecurity, e-commerce, and SaaS scored
perfectly (small samples, but directional). This is not noise — it
suggests AIRS's evidence assembly works better for some industries than
others.

**2. The crypto miss is systematic, not random.** All three L1
blockchain sessions (Bitcoin, Ethereum, Solana) were rated BEARISH on
2026-08-14. All three rallied +22% to +32% over the following 30 days.
Every single one scored -1.0 (maximum penalty).

This is the single largest and most consistent error in the audit. It
is also the clearest instance of the magnitude/direction bug: all three
assets carry high beta (1.5–2.4), and beta was being counted as a
bearish directional signal. High-beta assets were pushed toward bearish
bias by evidence that has nothing to do with direction.

**Action:** Beta was removed from directional claims on 2026-09-14
(commit `fix(hypothesis)`). Re-run the crypto watchlist after Phase 9.5
to verify the bias has corrected.

---

## Diagnosis: Magnitude vs Direction Category Error

The audit surfaced a systematic bug that affects the Hypothesis Engine.

The engine classifies evidence into three buckets — `bullish`,
`bearish`, `neutral` — by summing strength values. This assumes every
metric in the Evidence Register is a *directional* signal.

It is not. Some metrics are *magnitude* signals — they describe how
much price moves, not which way.

**Correctly classified (directional):**
- trend, momentum, MACD, RSI extremes, returns, news signals

**Misclassified (magnitude, treated as direction):**
- beta, risk_score, drawdown, volatility_regime, volatility

The misclassified metrics were contributing to directional claims.
Specifically:

| Metric            | Direction bucket | Strength | Behavior |
|-------------------|------------------|----------|----------|
| beta (0.5–1.0)    | bullish          | 0.35     | Low-volatility assets got +bullish weight |
| beta (> 1.5)      | bearish          | 0.45     | High-volatility assets got +bearish weight |
| risk_score (>0.4) | bearish          | 0.75     | High-risk assets got +bearish weight |
| drawdown (>0.2)   | bearish          | 0.50     | Large drawdowns got +bearish weight |
| volatility_regime | bearish          | 0.45     | Elevated volatility got +bearish weight |
| volatility        | neutral          | 0.30     | Stable volatility got +neutral weight |

The cumulative effect: **volatile assets were systematically biased
toward bearish.** Every high-beta name carried ~0.45 extra bearish
weight regardless of its actual directional evidence.

**Fix status (as of 2026-09-14):**
- ✅ Beta removed from `_assess_evidence()` in `reports/hypothesis.py`
- ✅ Beta added to `agents/risk.py` as a risk-side metric
- ⏳ risk_score, drawdown, volatility_regime, volatility — pending
  Phase 9.5

**Design principle recorded:** Decision 037 in
`docs/architecture/DECISIONS.md`.

---

## What This Baseline Implies for Phase 9.5

Three priorities, in order:

**1. Complete the magnitude/direction split.** Remove the four remaining
misclassified metrics from directional claims. Move them to the Risk
Agent. Re-run the audit and measure the delta against this baseline.

**2. Recalibrate uncertainty.** If the Low-uncertainty inversion
persists after Priority 1, the uncertainty formula in
`reports/hypothesis.py` `_compute_uncertainty()` is measuring the wrong
thing. Investigate the Scarcity/Conflict/Coverage weighting.

**3. Re-bucket evidence strength.** Thresholds in `compute_evidence_strength()`
are not discriminating. Fix or replace.

**Out of scope for Phase 9.5** (but recorded for context):
- Business Agent non-determinism (same ticker, two runs, different bias)
- Startup outcome proxies (Phase 11 — no price-based scoring possible)
- Sector-specific calibration (needs more sessions per sector)

---

## How to Compare Against This Baseline

When running a future audit:

```bash
python main.py --audit
```
## Compare the output against this document

### Overall avg score

Did it move toward 0 or away from it?

### By uncertainty level

Did the inversion resolve?

### By evidence strength

Are there still only one bucket?

### By sector

Did crypto and consumer-tech improve?

Any change is data. A regression is not a failure — it means the fix  
did not work as expected, which is equally informative.

## Metadata

| Field | Value |
|---|---|
| Audit run by | `python main.py --audit` |
| Sessions in DB at audit | 30 (ids 7–36) |
| Sessions scored | 23 |
| Sessions skipped | 7 (startups, no ticker) |
| DB file | `airs.db` |
| Backup | `airs.db.backup_20260914_193314` |
| Related decisions | Decision 037 |
| Related commits | `fix(hypothesis): stop using beta as a directional signal`, `feat(risk): surface market beta as a risk dimension` |
| Follow-up | Phase 9.5 — magnitude/direction split, uncertainty recalibration, evidence re-bucketing |

Baseline recorded 2026-09-14. Next audit will supersede this document.

The value of this baseline is not the number. It is the ability to  
measure whether the next number is better.
