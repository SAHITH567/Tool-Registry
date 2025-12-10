# Tool Registry + Graph Engine (Simple) - Humanized BTech Fresher Version

This repository is a compact FastAPI project built as a small capstone/demo by a BTech fresher (Sahith).
It demonstrates a minimal **tool registry** and a **graph workflow engine** (nodes -> edges -> state).
The code is written with clear comments, simple architecture, and an emphasis on explainability —
so a recruiter or interviewer can read through quickly and run it locally.

----
## Quick personal note (who made this)
Hi — I'm **Sahith**, a final-year BTech student. I built this small demo to show how a pipeline engine works and to practice designing simple backend workflows. I originally tried a recursive chunker which caused an index bug (learned about edge-cases and decided to keep it simple). This repo is intentionally readable so I can explain each part during interviews.

### What I found hard (short)
- Getting async/sync tool calls right — I had race conditions first.
- Deciding when to stop refining the summary — I added a max-iteration cap.
- I want to add unit tests and CI next (listed in TODO).

### Quick run instructions (for recruiters / reviewers)
1. Create a virtual environment (recommended) and install:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Start the app:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Open the API docs (interactive) at:
   ```
   http://127.0.0.1:8000/docs
   ```
4. Try the demo:
   - `POST /summarize` with JSON `{"text":"Long text ..."}`
   - `GET /tools` to see registered tools

### Example run (copy-paste)
Summarize a sample text (curl):
```bash
curl -X POST "http://127.0.0.1:8000/summarize"           -H "Content-Type: application/json"           -d '{"text":"<paste a few paragraphs here>", "chunk_size":500, "max_sentences_per_chunk":2, "final_max_length":400}'
```
Response keys: `final_summary` and `full_state`.

----
## What is included (human-friendly)
- `app/` : application package
  - `main.py` : FastAPI app with endpoints to run the engine and a summarization demo
  - `engine.py` : GraphEngine that executes nodes and handles branching
  - `tools.py` : Tool registry + simple builtin tools (chunk, summarize, merge, refine)
  - `workflows.py` : Example nodes implementing Summarization + Refinement (Option B)
  - `schemas.py` : simple Pydantic request models

- `README.md` (this file)
- `requirements.txt` : Python requirements for quick setup
- `.gitignore`

----
## Quick TODO (for reviewers)
- add unit tests (pytest)
- replace naive summarizer with LLM/transformer
- small frontend for demonstration

----
### Changelog (short)
- 2025-12-11: Added personal notes, TODO, sample input, and improved refine loop. - Sahith

----
Thank you for reviewing — this is built to be easy to run and inspect.
