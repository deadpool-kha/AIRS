# DECISIONS.md

# Engineering Decision Log

This file records important technical decisions and the reasoning behind them.

---

# Decision 001

## Use Python as primary language

Date:

July 2026

Decision:

Use Python for backend and AI development.

Reason:

* Strong ecosystem for AI and data science
* Good libraries for finance and ML
* Faster development speed

---

# Decision 002

## Use local LLMs instead of paid APIs initially

Decision:

Use Ollama with open-source models.

Reason:

* Project budget is $0
* Avoid API token costs
* Demonstrate local AI capability

---

# Decision 003

## Use SQLite initially

Decision:

Start with SQLite instead of PostgreSQL.

Reason:

* Zero setup
* Enough for MVP
* Easy local development

Future:

Migrate if scale requires it.

---

# Decision 004

## Do not build a generic chatbot

Decision:

Focus on investment research workflow.

Reason:

Generic chatbots are common and provide little differentiation.

The value comes from:

* data pipelines
* workflow automation
* analysis quality
* domain application

---

# Decision 005

## Use controlled agent loops

Decision:

Use a defined research workflow instead of uncontrolled autonomous agents.

Reason:

Improves:

* reliability
* debugging
* cost control
* evaluation
