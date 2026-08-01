# LEARNING.md

# Knowledge Capture Log

## 2026-07-19: Agent Loop Basics

Learned:

An agent loop consists of:
- state
- tools
- evaluation
- stopping condition



Application to AIRS:
- State = research progress dict (entity, iteration, agent_outputs)
- Tools = [fetch_stock, fetch_github, fetch_news, analyze_quant, analyze_technical]
- Evaluation = Critic Agent reviews research quality
- Stopping condition = max 3 iterations OR confidence threshold met

---

## 2026-07-20: Loop Engineering

Learned:

Loop engineering shifts AI from one-shot prompting to automated, self-improving systems.

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

---

## 2026-07-23: Building Business and Risk Agents

Learned:

Business Agent design:
- RSS is the simplest news source for MVP (no API keys, no scraping)
- Ollama qwen2.5:7b on GTX 1060 takes 60-90s for 2 prompts
- JSON extraction from LLM requires cleanup (strip markdown, handle parse errors)
- Graceful fallback when Ollama unavailable is critical for UX

Risk Agent design:
- Rules-based analysis is faster and more transparent than LLM for risk
- Cross-agent contradiction detection adds real value (e.g., price up but ecosystem down)
- Blind spot detection (all-positive warning) prevents confirmation bias
- Severity classification makes risks actionable

Hypothesis engine refinement:
- 5% minimum floor prevents 0% probabilities (DDScore #13)
- Risk Agent input dramatically improves bear case realism (5% → 18% for AAPL)
- Evidence must be shared across hypotheses, not siloed

Source: Personal experience building agents #6, #7

---

## 2026-07-23: Ollama Performance on Consumer Hardware

Learned:

- qwen2.5:7b (4.7 GB) fits in GTX 1060 6GB but runs slowly
- Exponential backoff retry (1s, 2s, 4s) handles timeouts gracefully
- num_predict=512 is generous; 256 would be faster with minimal quality loss
- temperature=0.3 keeps outputs factual for analysis tasks
- Ollama must be running (ollama serve) before script starts

Source: Testing Business Agent on development machine

---
---

## 2026-07-26: Building Critic Agent and Cross-Agent Integration

Learned:

Critic Agent design:
- Rule-based evaluation is fast and transparent — every gap has a clear trigger
- LLM enhancement adds value ONLY when gaps exist (skip if complete)
- Cross-agent checks find contradictions humans miss (quant confident + risk high)
- Mandatory iteration on HIGH risk prevents premature finalization

Hypothesis engine refinement v2:
- Minimum floor (5%) prevents 0% but is intellectually empty without evidence
- Risk Agent output must feed into bear case to satisfy DDScore evidence register
- Re-normalization after adding evidence keeps probabilities valid (sum to 1.0)
- Bear case jumped from 5% → 25% for AAPL once risks were included

Integration complexity:
- 5 agents now run in sequence: Quant → Technical → Business → Risk → Critic → Hypotheses
- Each agent depends on previous outputs — order matters
- Critic output affects loop behavior (iterate vs complete)
- Debugging requires tracing data flow across 5 files

Source: Personal experience building agents #8 and integrating cross-agent validation

---

## 2026-07-26: When "Working" Is Not Enough

Learned:

First Critic implementation reported quality 1.0 (perfect) while Risk said HIGH.
- Code was "working" but logically wrong
- The bug: Critic checked "did agents run?" not "did agents find problems?"
- Fixed by adding cross-agent checks: high risk + low iteration = gap

Hypothesis engine showed 5% bear with NO evidence.
- Minimum floor was hiding missing integration
- Fixed by wiring Risk Agent output into bear case
- Now bear case has real evidence and realistic probability

Lesson: Test outputs for semantic correctness, not just absence of errors.

Source: Debugging Critic and Hypothesis integration

---

## 2026-07-30: Building the Loop Controller

Learned:

Meaningful iteration requires changing inputs.

Simply re-running the same agents with the same parameters does not improve research quality—it only repeats the same computation.

Application to AIRS:
- Loop Controller only re-runs agents whose inputs can change
- Quant Agent benefits from iterative refinement
- Business and Technical Agents remain single-shot unless their inputs change
- Future iterations should mutate search breadth, lookback period, or analysis depth

Source: Personal experience implementing Issue #9

---

## 2026-07-30: RSS Is a Live Feed, Not a Historical Database

Learned:

RSS feeds only expose current articles.

They cannot answer questions such as "show me news from six months ago."

Historical news requires:
- paid news APIs
- archived datasets
- web scraping archives

Application to AIRS:
- Business Agent performs a single analysis over current news
- Later iterations should not repeatedly analyze identical RSS data

Source: Research while implementing Business Agent iteration

---

## 2026-07-30: Constrain Local LLMs to Existing Evidence

Learned:

Small local LLMs tend to hallucinate when asked to "find" new insights from unchanged data.

Better prompts ask the model to evaluate existing evidence rather than invent new evidence.

Examples:
- "Which signal has the weakest supporting evidence?"
- "Which conclusion has the lowest confidence?"

Avoid prompts such as:
- "Find hidden contradictions."
- "Discover additional risks."

Application to AIRS:
- Business Agent remains evidence-driven rather than speculative
- Future prompt improvements should strengthen reasoning without introducing new unsupported claims

Source: Testing Qwen2.5:7b during Loop Controller development

---

## 2026-07-30: Python Lambda Capture in Loops

Learned:

Lambdas created inside loops capture variables by reference, not by value.

Incorrect:

```python
for name in agents:
    runners[name] = lambda: run(name)
```

Every lambda ends up using the final value of `name`.

Correct:

```python
for name in agents:
    runners[name] = lambda n=name: run(n)
```

Using a default argument captures the current value for each lambda.

Application to AIRS:
- Prevented subtle bugs while building the Loop Controller's agent dispatch table

Source: Debugging early Loop Controller prototypes

---

## 2026-07-30: Database Constraints Document Valid State

Learned:

SQLite `CHECK` constraints improve both data integrity and documentation.

Example:

```sql
CHECK(status IN ('running', 'completed', 'failed'))
```

Benefits:
- prevents invalid values
- catches programming mistakes early
- documents allowed states directly in the schema

Application to AIRS:
- Used for execution state validation in the `loop_states` table

Source: SQLite documentation and implementation experience

## 2026-07-31: Checklist Loops Are Not Adaptive Loops

Learned:

The difference between a treadmill and an analyst:

**Treadmill (old system):**
- Asks the same question every iteration: "Do you have all 17 features?"
- Produces the same answer for every stock: missing 7, then 4, then 0
- Halt condition is pre-ordained: always iteration 3
- "Confidence: 100%" means checklist complete, not "we are certain"

**Analyst (new system):**
- Asks different questions per iteration:
  - Iteration 1: "Can I form a coherent view?"
  - Iteration 2: "Did deeper data change the story?"
  - Iteration 3: "What contradictions remain unresolved?"
- Halt condition is responsive: AAPL stopped at iteration 1, ORCL might need 3
- Dashboard shows what we actually know: Data Quality, Coverage, Agreement, Stability

Key insight:
**Features are means, not ends.** The loop should exist to answer investment questions, not to collect features. If you can form a directional view with 10 features, you don't need the other 7.

Application to AIRS:
- Critic now has 6 phases, not 1 checklist
- Hypotheses show directional bias + uncertainty, not fake probabilities
- Loop halts when the story is coherent, not when the checklist is full

Source: Debugging the old loop and redesigning Issue #9b+

---

## 2026-07-31: "Confidence" Is a Dangerous Word in Financial Software

Learned:

"Confidence: 100%" is one of the most misleading outputs a system can produce.

Old system:
- Confidence = checklist coverage percentage
- 100% meant "you have all 17 features"
- Users would read it as "we are certain about this investment"
- This is dangerous — it conflates structural completeness with epistemic certainty

New system:
- No single "confidence" number
- Dashboard shows 4 dimensions independently
- Uncertainty is explicit and factorized (Scarcity, Conflict, Coverage)
- Users can see *why* we are or aren't sure

Lesson: If you can't explain exactly how a number was computed, don't show it to investors.

Application to AIRS:
- Killed the `confidence` float in Critic output
- Replaced with `dashboard` dict
- Hypotheses show `directional_bias` and `uncertainty` separately

Source: Redesigning Critic and Hypothesis engines for Issue #9b+

---

## 2026-07-31: The Base Case Is Not a Garbage Can

Learned:

In three-way probability models (Bull + Bear + Base = 100%), the Base case becomes a mathematical dumping ground.

Example:
- Bull: 80%, Bear: 15% → Base gets 5%
- But that 5% might represent:
  - Genuine neutral evidence (RSI 50, stable volatility)
  - OR "we don't know" (missing data)
  - OR mathematical leftover from normalization

These are three completely different things. Lumping them together makes the output unreadable.

Solution:
- Separate directional conviction (bullish vs bearish) from uncertainty
- Base case only contains explicitly neutral signals
- Uncertainty is its own score with its own factors

Application to AIRS:
- Hypothesis engine no longer normalizes to 100%
- Base case only gets signals tagged as "neutral" (RSI 40-60, moderate risk, etc.)
- Uncertainty score explains how much we don't know

Source: Redesigning `reports/hypothesis.py` for Issue #9b+