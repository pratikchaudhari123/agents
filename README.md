# Krishna Jarvis

Local owner-approved AI coding agent. Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
open -e .env
python app.py
```

Open http://127.0.0.1:8765. Set your API key in .env, never commit it. Set JARVIS_WORKSPACE to an authorized project directory. Commands execute with your OS user permissions, not a sandbox: review every approval. The model can propose new code and integrations but cannot automatically authorize external accounts. Chat history is stored locally and sent to the API for context. This prototype has no hard API budget, background workers, automatic tool registration, or production security guarantee. Pending approvals are in memory; restarting mid-approval may require resetting the local chat database.
