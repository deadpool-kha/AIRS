# DECISIONS.md

# Engineering Decision Log

This file records important technical decisions and the reasoning behind them.

---

# Decision 001

## Use Python as primary language

Date: 2026-07-19

Decision:

Use Python for backend and AI development.

Reason:

* Strong ecosystem for AI and data science
* Good libraries for finance and ML
* Faster development speed

Rejected alternatives:
* TypeScript/Node.js (less mature for data science)
* Go (faster but less library support for AI)
* Rust (too complex for MVP)

Revisit if: Performance becomes critical at scale

---

# Decision 002

## Use local LLMs instead of paid APIs initially

Date: 2026-07-19

Decision:

Use Ollama with open-source models.

Reason:

* Project budget is $0
* Avoid API token costs
* Demonstrate local AI capability
* Data privacy (no data leaves machine)

Rejected alternatives:
* OpenAI GPT-4 (costs money)
* Anthropic Claude (costs money)
* Google Gemini (free tier has limits)

Revisit if: Local models insufficient for report quality

---

# Decision 003

## Use SQLite initially

Date: 2026-07-19

Decision:

Start with SQLite instead of PostgreSQL.

Reason:

* Zero setup
* Enough for MVP
* Easy local development
* Portable (single file)

Rejected alternatives:
* PostgreSQL (requires installation and configuration)
* MongoDB (overkill for structured data)
* Redis (not persistent enough)

Revisit if: Scale requires concurrent writes or complex queries

---

# Decision 004

## Do not build a generic chatbot

Date: 2026-07-19

Decision:

Focus on investment research workflow.

Reason:

Generic chatbots are common and provide little differentiation.

The value comes from:

* data pipelines
* workflow automation
* analysis quality
* domain application

Rejected alternatives:
* Generic RAG chatbot (too common, not impressive)
* Simple Q&A system (doesn't demonstrate engineering)

---

# Decision 005

## Use controlled agent loops (loop engineering)

Date: 2026-07-20

Decision:

Use a defined research workflow with explicit iteration instead of uncontrolled autonomous agents.

Reason:

Improves:

* reliability
* debugging
* cost control
* evaluation
* transparency

Inspired by Andrew Ng's loop engineering concept.

The loop: Plan → Research → Analyze → Critique → (Iterate or Complete)

Rejected alternatives:
* Uncontrolled autonomous agents (unpredictable, hard to debug)
* Single-pass analysis (no quality improvement)
* Pure LLM chain (expensive, unreliable)

Revisit if: Need more autonomous behavior for advanced use cases

---

# Decision 006

## Use 4 specialized agents + 1 critic agent

Date: 2026-07-20

Decision:

Quant, Technical, Business, Risk agents + Critic agent.

Reason:

* Enough complexity to demonstrate multi-agent system
* Each has clear, distinct responsibility
* Feasible to build in 3-4 weeks
* Covers key dimensions of investment research

Rejected alternatives:
* 2 agents (too simple)
* 6+ agents (scope creep, never finish)
* Single monolithic agent (not modular)

Revisit if: Need more specialized analysis (e.g., ESG, macro)

---

# Decision 007

## Use GitHub Issues for all work tracking

Date: 2026-07-20

Decision:

Every task, bug, and feature gets a GitHub issue.

Reason:

* Clear history of decisions and progress
* Easy to reference in commits
* Demonstrates professional workflow
* Helps with portfolio storytelling

Rejected alternatives:
* Trello (external, not tied to code)
* Jira (overkill for solo project)
* Mental tracking (unreliable, not visible)

Revisit if: Project grows to 3+ contributors

---

# Decision 008

## Use INSERT OR REPLACE for idempotent storage

Date: 2026-07-20

Decision:
Use SQLite's INSERT OR REPLACE instead of INSERT.

Reason:
- Prevents crashes when re-fetching same ticker+date
- Makes operations idempotent (safe to re-run)
- Simpler than checking existence first

Rejected alternatives:
- SELECT then INSERT (more queries, race conditions)
- INSERT with try/except (ugly, exception-driven logic)

Revisit if: Need to preserve historical versions of same data

---

# Decision 009

## Use json.dumps for flexible schema columns

Date: 2026-07-20

Decision:
Store agent_outputs and critic_feedback as JSON strings.

Reason:
- SQLite has no native dict/list types
- JSON is human-readable and portable
- Avoids schema changes when agent outputs evolve

Rejected alternatives:
- Separate table per agent (too many tables, complex joins)
- Pickle (Python-only, not human-readable)
- Multiple columns per metric (rigid, breaks on changes)

Revisit if: Need to query inside JSON (then use PostgreSQL JSONB)

---

# Decision 010

## Separate fetcher from database (Adapter Pattern)

Date: 2026-07-20

Decision:
data/fetcher.py only fetches. data/db.py only stores.

Reason:
- If yfinance breaks, change one file
- If we switch to PostgreSQL, change one file
- Each module has one reason to change (Single Responsibility Principle)

Rejected alternatives:
- Combined fetch+save function (tight coupling)
- Direct yfinance calls in main.py (no abstraction)

Revisit if: Need transaction-level fetch+save atomicity