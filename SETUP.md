# SETUP.md

# AIRS Development Setup

## Requirements

Python 3.11+

Git

Ollama

---

# Installation

Clone repository:

```
git clone <repository-url>
```

Enter directory:

```
cd AIRS
```

Create virtual environment:

```
python -m venv venv
```

Activate:

Windows:

```
venv\Scripts\activate
```

Install dependencies:

```
pip install -r requirements.txt
```

---

# Local LLM Setup

Install Ollama.

Download model:

```
ollama pull qwen2.5:7b
```

Test:

```
ollama run qwen2.5:7b
```

---

# Running Project

Backend:

```
python main.py
```

Frontend:

```
streamlit run app.py
```

---

# Environment Variables

Create:

```
.env
```

Example:

```
API_KEY=
DATABASE_PATH=
```

Never commit `.env`.
