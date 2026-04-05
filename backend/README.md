# Backend (FastAPI)

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check: `http://localhost:8000/health`

