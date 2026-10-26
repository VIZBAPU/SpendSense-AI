# SpendSense

Bank statement categorizer and anomaly detector with a local LLM (synthetic data only).

> 🚧 Work in progress. The full README (screenshots, architecture, accuracy results)
> comes at release v1.0.0. Planning and design docs are in [`docs/`](docs/).

## Run it locally

**Prerequisites:** Docker Desktop (running), Git. About 6 GB of free disk for the LLM model.

1. **Configure:** copy `.env.example` to `.env` and set your own password in **both**
   `POSTGRES_PASSWORD` and `DATABASE_URL`.
   If the password contains URL-special characters (`@ : / # ? %`), URL-encode them in
   `DATABASE_URL` only (e.g. `@` → `%40`), or simply avoid them.
2. **Start everything:**
   ```bash
   docker compose up -d --build
   ```
3. **Download the LLM model (one-time, ~4.7 GB):**
   ```bash
   docker compose exec ollama ollama pull qwen2.5:7b
   ```
4. **Check:**
   - API health: http://localhost:8000/health → `{"status":"ok","db":"up","ollama":"up",...}`
   - API docs: http://localhost:8000/docs
   - Web app: http://localhost:5173

| Service | Port | What it is |
|---|---|---|
| `web` | 5173 | React + TypeScript (Vite) |
| `api` | 8000 | FastAPI |
| `db` | 5432 | PostgreSQL 16 |
| `ollama` | 11434 | Local LLM server |

## Generate synthetic data

All data is fake. The generator writes 6 months of a freelancer's transactions (~570 rows)
with planted anomalies and an answer key:

```bash
cd backend
.venv\Scripts\python -m scripts.generate_data --seed 42
```

Output (gitignored) in `data/generated/`:
- `statement.csv`: Format B bank export (`Date, Description, Debit, Credit`, dates `MM/DD/YYYY`)
- `ground_truth.csv`: the correct category for every row
- `anomalies.json`: the 12 planted anomalies (3 × z-score, duplicate, new-merchant, subscription increase)

The same seed always produces the same files.

## Backend checks (lint + tests)

```bash
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"     # Windows
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m pytest -v
```
(On macOS/Linux, use `.venv/bin/python` instead of `.venv\Scripts\python`.)

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `/health` shows `"db":"down"`, logs say *failed to resolve host* | Special character (e.g. `@`) in the password breaks `DATABASE_URL` | URL-encode it in `DATABASE_URL` (`@` → `%40`) |
| `password authentication failed` after changing the password | Postgres only reads `POSTGRES_PASSWORD` when it first creates its data volume | Dev only (deletes DB data): `docker compose stop api db`, `docker compose rm -f db`, `docker volume rm spendsense-ai_pgdata`, `docker compose up -d db api`. ⚠️ Don't use `down -v`; it also deletes the downloaded model |
| `"ollama":"down"` | Ollama container not running, or still starting | `docker compose up -d ollama`; the app still works without it (no LLM features) |
