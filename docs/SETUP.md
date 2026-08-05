# SETUP.md

# AIRS Development Setup

> **Version:** 0.3.7

---

## Requirements

Before starting development, install:

- Python 3.11+
- Git
- Ollama

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/deadpool-kha/AIRS.git
cd AIRS
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Local LLM Setup

1. Install Ollama: https://ollama.com
2. Download the recommended model:

```bash
ollama pull qwen2.5:7b
```

3. Test the model:

```bash
ollama run qwen2.5:7b "Hello, are you working?"
```

Expected result: The model responds with a greeting.

4. Start the Ollama server (keep running in a separate terminal):

```bash
ollama serve
```

---

## Optional: PDF Export Dependencies

PDF generation requires additional packages. They are optional — AIRS works without them, but `--pdf` will be skipped.

### Python Packages

```bash
pip install weasyprint markdown
```

### Windows: GTK+ Runtime

WeasyPrint requires GTK+ system libraries on Windows.

Download and install from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

If GTK+ is missing, `--pdf` will log a warning and only Markdown will be generated. No crash.

### macOS

```bash
brew install pango libffi
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
```

---

## Verify Installation

After setup, verify the environment:

```bash
python -c "import pandas, numpy, yfinance; print('Core dependencies OK')"
python -c "import sqlite3; print('SQLite OK')"
python -c "import ollama; print('Ollama Python client OK')"
python -c "import jinja2; print('Jinja2 OK')"
ollama --version
```

Expected output:

- Dependency checks pass
- Version numbers are displayed
- No errors occur

---

## Running the Project

### Full Evidence-Driven Research Loop

```bash
python main.py --entity AAPL --ticker AAPL --hypotheses
```

### With GitHub Repository

```bash
python main.py --entity AAPL --ticker AAPL --repo apple/swift --hypotheses
```

### With PDF Export

```bash
python main.py --entity AAPL --ticker AAPL --repo apple/swift --hypotheses --pdf
```

### Cryptocurrency with Repository

```bash
python main.py --entity bitcoin --ticker BTC-USD --repo bitcoin/bitcoin --hypotheses
```

### Open-Source Project (No Market Data)

```bash
python main.py --entity rust-lang --repo rust-lang/rust --hypotheses
```

### Single-Shot Modes

```bash
# Quantitative analysis only
python main.py --entity AAPL --quant-only

# Technical analysis only
python main.py --repo bitcoin/bitcoin --technical-only

# Business analysis only
python main.py --entity NVIDIA --business-only

# With source tracking
python main.py --entity AAPL --quant-only --show-sources
```

### Data Period Selection

```bash
python main.py --entity AAPL --quant-only --period 6mo
```

Available periods: `1mo`, `3mo` (default), `6mo`, `1y`

---

## Environment Variables

Create a file `.env` in the project root:

```env
# Optional: GitHub token for higher rate limits
GITHUB_TOKEN=

# Optional: Custom database path
DATABASE_PATH=
```

Never commit `.env` files to GitHub.

---

## .gitignore Template

Create `.gitignore` in the project root:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.venv/
venv/

# Environment
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/

# Operating System
.DS_Store
Thumbs.db

# Reports
reports/output/

# Documentation exceptions
*.md
!README.md
!docs/**/*.md
```

---

## Troubleshooting

### Ollama on Windows

If the Ollama service does not start:

1. Check Windows Services for Ollama.
2. Start Ollama manually:

```bash
ollama serve
```

3. Run it in a separate terminal.

### Ollama Timeout / Business Agent Skipped

If you see:

```text
⚠️  Business Agent skipped: Connection error
     (Start Ollama with: ollama serve)
```

Ensure `ollama serve` is running before starting AIRS. The Business Agent requires an active Ollama connection for news summarization.

### yfinance Errors

If yfinance returns empty data:

- Check internet connection.
- Try a different ticker.
- Some tickers may not have available data.

yfinance is unofficial and may temporarily break due to external changes.

### SQLite Locked

If the database is locked:

- Close SQLite browser tools.
- Ensure no other Python process is using the database.
- Delete the `.db-journal` file if it exists.

### PDF Generation Skipped

If you see:

```text
PDF generation skipped: weasyprint not installed.
Install with: pip install weasyprint markdown
```

Install the optional dependencies:

```bash
pip install weasyprint markdown
```

On Windows, also install the GTK+ runtime (see "Optional: PDF Export Dependencies" above).

### GitHub Rate Limit

If Technical Agent returns 403 errors:

- You have hit the unauthenticated rate limit (60 requests/hour).
- Wait one hour, or provide a GitHub token in `.env`:

```env
GITHUB_TOKEN=ghp_your_token_here
```

---

## requirements.txt

```txt
# Core data processing
pandas>=2.0.0
numpy>=1.24.0

# Financial data (free, no API key)
yfinance>=0.2.28

# HTTP requests
requests>=2.31.0

# Configuration
python-dotenv>=1.0.0

# Data validation
pydantic>=2.0.0

# Web framework (future use)
fastapi>=0.100.0
uvicorn>=0.23.0

# Local LLM
ollama>=0.1.0

# Report templates
jinja2>=3.1.0

# Optional: PDF export
# weasyprint>=60.0
# markdown>=3.5.0

# GitHub API
PyGithub>=2.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0

# RSS parsing (for Business Agent)
feedparser>=6.0.0

# Date handling
python-dateutil>=2.8.0
```

`weasyprint` and `markdown` are commented out by default because they require system-level dependencies (GTK+ on Windows). Uncomment after installing the system requirements.

---

## Documentation Structure

After setup, the documentation is organized as follows:

```text
docs/
├── research/
│   ├── DESIGN_PHILOSOPHY.md
│   ├── EVALUATION.md
│   ├── CASE_STUDIES.md
│   └── LIMITATIONS.md
├── architecture/
│   ├── ARCHITECTURE.md
│   └── DECISIONS.md
├── development/
│   ├── ROADMAP.md
│   ├── CHANGELOG.md
│   ├── CURRENT_TASK.md
│   ├── LEARNING.md
│   └── PROJECT_NOTES.md
└── SETUP.md
```

<div align="center">

**AIRS v0.3.7 — Evidence-Driven Investment Research Infrastructure**

</div>