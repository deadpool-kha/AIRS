# SETUP.md

# AIRS Development Setup

## Requirements

Before starting development, install:

- Python 3.11+
- Git
- Ollama

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
```

## Enter Project Directory

```bash
cd AIRS
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Local LLM Setup

Install Ollama:

https://ollama.com

Download the recommended model:

```bash
ollama pull qwen2.5:7b
```

Test the model:

```bash
ollama run qwen2.5:7b "Hello, are you working?"
```

Expected result:

The model responds with a greeting.

---

# Verify Installation

After setup, verify the environment:

```bash
python -c "import pandas, numpy, yfinance; print('Core dependencies OK')"

python -c "import sqlite3; print('SQLite OK')"

python -c "import ollama; print('Ollama Python client OK')"

ollama --version
```

Expected output:

- Dependency checks pass
- Version numbers are displayed
- No errors occur

---

# Running the Project

Example:

```bash
python main.py --entity "AAPL"
```

---

# Environment Variables

Create a file:

```text
.env
```

Example:

```env
# Optional: GitHub token for higher rate limits
GITHUB_TOKEN=

# Optional: Custom database path
DATABASE_PATH=
```

Never commit `.env` files to GitHub.

---

# .gitignore Template

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
reports/

# Documentation exceptions
*.md
!README.md
!docs/*.md
```

---

# Troubleshooting

## Ollama on Windows

If the Ollama service does not start:

1. Check Windows Services for **Ollama**.
2. Start Ollama manually:

```bash
ollama serve
```

Run it in a separate terminal.

---

## yfinance Errors

If yfinance returns empty data:

- Check internet connection.
- Try a different ticker.
- Some tickers may not have available data.
- yfinance is unofficial and may temporarily break due to external changes.

---

## SQLite Locked

If the database is locked:

- Close SQLite browser tools.
- Ensure no other Python process is using the database.
- Delete the `.db-journal` file if it exists.

---

# requirements.txt

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