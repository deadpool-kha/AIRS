# LEARNING.md

# Knowledge Capture Log

## 2026-07-19: Agent Loop Basics

Learned:

An agent loop consists of:
- state
- tools
- evaluation
- stopping condition

Source: Andrew Ng's talks on AI agent design

Application to AIRS:
- State = research progress dict (entity, iteration, agent_outputs)
- Tools = [fetch_stock, fetch_github, fetch_news, analyze_quant, analyze_technical]
- Evaluation = Critic Agent reviews research quality
- Stopping condition = max 3 iterations OR confidence threshold met

---

## 2026-07-20: Loop Engineering

Learned:

Loop engineering (Andrew Ng) shifts AI from one-shot prompting to automated, self-improving systems.

Key insight: The system critiques its own output and iterates to improve quality.

Application to AIRS:
- Critic Agent evaluates all agent outputs
- Identifies specific gaps (not just "bad")
- Loop Controller acts on critique to target next iteration
- Max 3 iterations prevents infinite loops

Benefits:
- Higher quality reports
- Transparent improvement process
- Demonstrates advanced AI engineering

---

## 2026-07-20: Separation of Concerns

Learned:

Database code and data fetching code should never be in the same file.

Why:
- If yfinance breaks, you only change fetcher.py
- If you switch from SQLite to PostgreSQL, you only change db.py
- Each module has one reason to change

Application to AIRS:
- `data/db.py` = only SQLite operations
- `data/fetcher.py` = only external API calls
- `agents/quant.py` = only quantitative analysis

---

## 2026-07-20: GitHub Issues for Solo Projects

Learned:

Even solo developers should use GitHub Issues.

Why:
- Creates a visible history of decisions
- Links commits to specific work
- Helps with portfolio storytelling
- Prevents "what was I doing?" moments

Application to AIRS:
- Every task gets an issue
- Branch names reference issues: `feature/#4-database-schema`
- Commit messages close issues: `Closes #4`