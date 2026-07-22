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

---

## 2026-07-20: Building lesson.py

Learned:
Writing a standalone script first, then splitting into modules, is easier than building modular from scratch.

Application to AIRS:
- Built lesson.py with fetch → analyze → save in one file
- Understood each piece before splitting into data/, agents/
- Now can explain every line in the "complex" project files

Source: Personal experience, guided by senior dev mentor

---

## 2026-07-20: Financial Metrics Implementation

Learned:
- pct_change() is vectorized (100x faster than Python loops)
- cummax() finds running peak for drawdown calculation
- Annualized volatility = daily_std * sqrt(252)
- Risk score combines multiple metrics into interpretable 0-1 scale

Application to AIRS:
- All Quant Agent metrics use these exact patterns
- Can now explain metrics to non-technical interviewers

Source: pandas documentation, quantitative finance basics

---

## 2026-07-21: Auditable Confidence Design

Learned:
Professional financial software requires traceability, not just results.

Key insight from DDScore feedback:
- "A report that looks confident but can't be verified is dangerous"
- Confidence must be decomposable: show WHY it's high or low
- Every claim needs a source: where did this number come from?
- Critic feedback must be append-only, not silently erased

Application to AIRS:
- Replaced flat confidence (0.85) with component breakdown
- Added source tracking to every metric (yfinance source, calculation method, timestamp)
- Built --show-sources flag for audit mode vs clean mode
- Designed critic_history table for immutable feedback

Source: GitHub Issue #13 feedback from DDScore at Playful Pixels Oy

---

## 2026-07-21: Responding to Professional Feedback

Learned:
How to engage with expert feedback without overcommitting.

Pattern:
1. Acknowledge the insight
2. Scope the implementation for MVP
3. Commit to principles long-term
4. Reference their work

This builds relationships and shows professional maturity.

Source: GitHub Issue #13, external contributor feedback

---

## 2026-07-21: API Discovery Method

Learned:
How to figure out what goes inside a function when you don't know the API.

Pattern:
1. Google the API documentation
2. Test the endpoint in browser (raw JSON)
3. Explore in interactive Python (type(), keys(), print())
4. Then write the function

Example: GitHub API
- Docs: docs.github.com/en/rest/commits/commits
- Browser test: https://api.github.com/repos/bitcoin/bitcoin/commits
- Python explore: response.json()[0]['commit']['message']
- Then build: get_commits(), get_repo_info(), etc.

Key insight:
Nobody memorizes APIs. Professionals discover them. The skill is exploration, not memorization.

Source: Personal experience, guided by senior dev mentor