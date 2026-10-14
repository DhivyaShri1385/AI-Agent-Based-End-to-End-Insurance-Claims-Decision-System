# ClaimIQ

Agentic AI-powered insurance claims automation platform. **Synthetic demo data only.**

## Status
Stage 2 of 16: Authentication, RBAC, Users and Policies.

## Prerequisites (Windows 10/11)
- Python 3.11 or 3.12 (tick "Add python.exe to PATH" during install)
- Node.js 20+ LTS
- VS Code

## Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```
API docs: http://127.0.0.1:8000/docs

## Frontend
```powershell
cd frontend
npm install
npm run dev
```
App: http://localhost:5173

## Tests
```powershell
cd backend ; pytest -v
cd ..\frontend ; npm test
```

## Stage 2: database and demo accounts
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python ..\scripts\seed_database.py
```
Demo accounts (synthetic; password `Demo@12345`):
`admin@example.com`, `adjuster1@example.com`, `adjuster2@example.com`,
`alice@example.com`, `bob@example.com`.
Set a real `SECRET_KEY` in `backend/.env` (see `.env.example`).

