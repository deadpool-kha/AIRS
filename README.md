# AIRS — Autonomous Investment Research System

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)
![Version](https://img.shields.io/badge/Version-0.3.8-blueviolet)

> **Evidence-driven research infrastructure. Not a stock predictor. Not a trading bot.**

AIRS automates the structured workflow of an investment research team: it collects evidence from market data, news, and code repositories; audits its own reasoning through deterministic evaluation; and generates transparent, traceable research memos.

**Created and maintained by [deadpool-kha](https://github.com/deadpool-kha)**

---

## What It Does

```bash
python main.py --entity AAPL --ticker AAPL --repo apple/swift --hypotheses --pdf
```

1. **Capability Probe** — Detects available research dimensions (Quant, Technical, Business)
2. **Bootstrap** — Business Agent reads news; Technical Agent reads GitHub
3. **Iterative Quant Analysis** — 3-month → 6-month → 1-year depth, tier by tier
4. **Critic Audit** — Rule-based 6-phase evaluation after every tier
5. **Adaptive Halt** — Stops early when evidence is coherent; continues when contradictory
6. **Hypothesis Engine** — Directional bias + explicit uncertainty (no fake probabilities)
7. **Investment Memo** — Professional Markdown report with optional PDF export

The loop is genuinely adaptive. Apple might halt at iteration 1; Bitcoin might need all 3.

---

## Live Example: Apple (AAPL)

```text
╔══════════════════════════════════════════════╗
║  AIRS  v0.3.8                                ║
║  Evidence-Driven Investment Research          ║
╚══════════════════════════════════════════════╝

AAPL  |  3 iterations  |  19 evidence items  |  max_iterations

Directional Bias: BEARISH
Uncertainty: 17% — Low
Halt: Circuit breaker hit. Returning best available analysis.

Report: reports/output/AAPL_20260813_043449.md
```

([View full example report →](reports/examples/AAPL_20260814_033706.md))

---

## Architecture

```text
                         User Request
                              │
                              ▼
                   Research Controller
                      (Loop Engine)
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
      Quant Agent       Technical Agent     Business Agent
   (Tiered: 3mo→6mo→1y)   (GitHub API)        (RSS + Ollama)
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
                    Evidence Register
                              │
                              ▼
                       Critic Agent
                  (6-Phase Rule-Based)
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    More Research Needed                 Hypothesis Engine
    (contradictions persist)          (Directional Bias +
                                          Uncertainty)
                                              │
                                              ▼
                                        Risk Agent
                                              │
                                              ▼
                                     Report Generator
                                    (Jinja2 → Markdown / PDF)
                                              │
                                              ▼
                                       Investment Memo
```

---

## Non-Negotiable Principles

| **Principle**             | **Implementation**                                                     |
| ------------------------- | ---------------------------------------------------------------------- |
| **Critic Agent**          | 100% rule-based. No LLM decides when to halt.                          |
| **Evidence Register**     | Single source of truth. Every claim traces to source, tier, raw value. |
| **Financial Analysis**    | Deterministic. No LLM computes statistics or indicators.               |
| **Hypothesis Generation** | Evidence-weighted, never normalized to 100%.                           |
| **Uncertainty**           | Independent from directional conviction.                               |

---

## Quick Start

```bash
git clone https://github.com/deadpool-kha/AIRS.git
cd AIRS

python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt

# Install Ollama: https://ollama.com
ollama pull qwen2.5:7b
ollama serve  # keep running in separate terminal
```

Run a single analysis:

```bash
python main.py --entity AAPL --ticker AAPL --repo apple/swift --hypotheses
```

Run a batch watchlist:

```bash
python main.py --watchlist tech_blue_chip --hypotheses
```

Audit historical accuracy (after 30 days):

```bash
python main.py --audit
```

See [SETUP.md](docs/SETUP.md) for detailed installation and troubleshooting.

---

## CLI Reference

| **Flag**         | **Description**                                                              |
| ---------------- | ---------------------------------------------------------------------------- |
| `--entity`       | Company or asset name                                                        |
| `--ticker`       | Stock/crypto ticker for quantitative analysis                                |
| `--repo`         | GitHub repository (`owner/repo`)                                             |
| `--hypotheses`   | Run full evidence-driven research loop                                       |
| `--watchlist`    | Batch category: `tech_blue_chip`, `tech_growth`, `crypto`, `startups`, `all` |
| `--sector`       | Tag session with canonical sector                                            |
| `--audit`        | Evaluate historical session accuracy                                         |
| `--pdf`          | Also generate PDF report                                                     |
| `--show-sources` | Display evidence provenance                                                  |

---

## Project Structure

```text
AIRS/
├── agents/           # Quant, Technical, Business, Risk, Critic
├── controller/       # Loop orchestration
├── core/             # Evidence Register
├── data/             # SQLite, fetcher, audit trail
├── reports/          # Hypothesis engine, report generator, templates
├── config/           # Watchlists, sectors
├── docs/             # Full documentation
├── main.py           # CLI entry point
└── requirements.txt
```

---

## Documentation

| **Document**                                                                      | **What It Covers**                                 |
| --------------------------------------------------------------------------------- | -------------------------------------------------- |
| [Design Philosophy](docs/research/DESIGN_PHILOSOPHY.md) | Why AIRS exists, core principles                   |
| [Architecture](docs/architecture/ARCHITECTURE.md)       | Full 7-layer system design                         |
| [Case Studies](docs/research/CASE_STUDIES.md)           | Real sessions: AAPL, Bitcoin, Rust, batch analysis |
| [Evaluation](docs/research/EVALUATION.md)               | How research quality is measured                   |
| [Limitations](docs/research/LIMITATIONS.md)             | Known boundaries                                   |
| [Decision Log](docs/architecture/DECISIONS.md)          | Engineering decisions                              |
| [Roadmap](docs/development/ROADMAP.md)                  | Phase-based development plan                       |
| [Changelog](docs/SETUP.md)                              | Installation, dependencies, troubleshooting        |

---

## Current Status

| **Phase** | **Feature**                            | **Status**                |
| --------- | -------------------------------------- | ------------------------- |
| 1-8       | Core loop, agents, report generator    | ✅ Complete                |
| 9         | Audit Trail & Backtesting              | ✅ Infrastructure complete |
| 9.5       | Audit polish, CSV export, trend graphs | 📅 Planned                |
| 10        | Streamlit web interface                | 📅 Planned                |

---

## Author & License

**Created and maintained by** [**deadpool-kha**](https://github.com/deadpool-kha)

This project is released under the [MIT License](/LICENSE).

> You are welcome to fork, modify, and build upon this project. If you do, please retain the original attribution and link back to this repository.

---

<div align="center">

**AIRS v0.3.8** — *Research should be explainable before it is persuasive.*

</div>

