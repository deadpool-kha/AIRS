#!/usr/bin/env python3
"""
setup_project.py

Creates the entire AIRS folder structure automatically.

Usage:
    python setup_project.py
    
Why this exists:
- Instead of manually creating folders in VS Code, run one script.
- Ensures consistent structure across environments.
- Self-documenting: the script IS the structure.
"""

import os
from pathlib import Path


# Define the folder structure as a list of paths
# These are relative to the project root
FOLDERS = [
    # Data layer
    "data",
    
    # Agent layer
    "agents",
    
    # Loop controller
    "controller",
    
    # Report generation
    "reports",
    
    # Utilities (Ollama client, helpers)
    "utils",
    
    # Tests
    "tests",
    
    # Frontend (future)
    "frontend",
]


# Define files that need to exist
# Key: file path, Value: initial content
FILES = {
    # Package init files (empty but required for imports)
    "data/__init__.py": "# data package\n",
    "agents/__init__.py": "# agents package\n",
    "controller/__init__.py": "# controller package\n",
    "reports/__init__.py": "# reports package\n",
    "utils/__init__.py": "# utils package\n",
    "tests/__init__.py": "# tests package\n",
    
    # Main entry point (we'll fill this in later)
    "main.py": '''#!/usr/bin/env python3
"""
main.py

Entry point for AIRS.

Usage:
    python main.py --entity "AAPL"
"""

import argparse


def main():
    parser = argparse.ArgumentParser(description="AIRS - Autonomous Investment Research System")
    parser.add_argument("--entity", type=str, required=True, help="Entity to analyze")
    args = parser.parse_args()
    
    print(f"Analyzing: {args.entity}")
    # TODO: Implement full workflow
    return 0


if __name__ == "__main__":
    exit(main())
''',
    
    # Placeholder for agent files
    "agents/quant.py": '''"""
agents/quant.py

Quant Agent: Numerical analysis of market data.
"""

def analyze(ticker, df):
    raise NotImplementedError("Quant Agent coming in Day 2")
''',
    
    "agents/technical.py": '''"""
agents/technical.py

Technical Agent: GitHub ecosystem health analysis.
"""

def analyze(repo):
    raise NotImplementedError("Technical Agent coming in Day 3")
''',
    
    "agents/business.py": '''"""
agents/business.py

Business Agent: News and business signal extraction.
"""

def analyze(entity, news_items):
    raise NotImplementedError("Business Agent coming in Day 4")
''',
    
    "agents/risk.py": '''"""
agents/risk.py

Risk Agent: Downside and weakness analysis.
"""

def analyze(agent_outputs):
    raise NotImplementedError("Risk Agent coming in Day 5")
''',
    
    "agents/critic.py": '''"""
agents/critic.py

Critic Agent: Research quality evaluation.
"""

def evaluate(agent_outputs, iteration):
    raise NotImplementedError("Critic Agent coming in Day 6")
''',
    
    # Placeholder for controller
    "controller/loop.py": '''"""
controller/loop.py

Loop Controller: Orchestrates the research workflow.
"""

class LoopController:
    def __init__(self, max_iterations=3):
        self.max_iterations = max_iterations
    
    def run(self, entity):
        raise NotImplementedError("Loop Controller coming in Day 7")
''',
    
    # Placeholder for report generator
    "reports/generator.py": '''"""
reports/generator.py

Report Generator: Creates investment memos.
"""

def generate(agent_outputs, critic_feedback, iteration_count):
    raise NotImplementedError("Report Generator coming in Day 8")
''',
    
    # Placeholder for Ollama client
    "utils/ollama_client.py": '''"""
utils/ollama_client.py

Ollama client wrapper for local LLM calls.
"""

def generate(prompt, model="qwen2.5:7b"):
    raise NotImplementedError("Ollama client coming in Day 9")
''',
    
    # Database placeholder
    "data/db.py": '''"""
data/db.py

Database layer. Coming in Day 1.
"""

def init_db():
    raise NotImplementedError("Database coming in Day 1")
''',
    
    "data/fetcher.py": '''"""
data/fetcher.py

Market data fetcher. Coming in Day 1.
"""

def fetch_stock_data(ticker, period="3mo"):
    raise NotImplementedError("Fetcher coming in Day 1")
''',
}


def create_folders():
    """Creates all folders in FOLDERS list."""
    for folder in FOLDERS:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  📁 {folder}/")


def create_files():
    """Creates all files with initial content."""
    for filepath, content in FILES.items():
        path = Path(filepath)
        
        # Only create if file doesn't exist (don't overwrite existing work)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            print(f"  📄 {filepath}")
        else:
            print(f"  ⏭️  {filepath} (already exists, skipping)")


def main():
    print("=" * 50)
    print("AIRS Project Setup")
    print("=" * 50)
    print()
    
    print("Creating folders...")
    create_folders()
    print()
    
    print("Creating files...")
    create_files()
    print()
    
    print("=" * 50)
    print("Done! Run 'python main.py --entity AAPL' to test.")
    print("=" * 50)


if __name__ == "__main__":
    main()