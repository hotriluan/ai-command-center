# CLAUDE.md

> **AI Command Center - Executive Dashboard Project**
> This file provides context, commands, and guidelines for Claude Code to work effectively on this project.

## 🏗️ Project Structure

- **Frontend**: Next.js (React) + Tailwind CSS + Recharts
  - Path: `./frontend`
  - Port: 3000
- **Backend**: FastAPI (Python) + SQLite + SQLAlchemy
  - Path: `./backend`
  - Port: 8000

## 🛠️ Common Commands

| Category | Description | Command |
|----------|-------------|---------|
| **Frontend** | Start Dev Server | `cd frontend && npm run dev` |
| | Build Production | `cd frontend && npm run build` |
| | Type Check | `cd frontend && npm run type-check` |
| | Lint | `cd frontend && npm run lint` |
| **Backend** | Start Dev Server | `cd backend && .\.venv\Scripts\python.exe -m uvicorn main:app --reload` |
| | Install Deps | `cd backend && pip install -r requirements.txt` |
| | Database Init | `cd backend && python -c "from database import init_db; init_db()"` |
| **Testing** | Verify Dashboard | `See .agent/workflows/dashboard-workflow.md` |

## 🌊 Workflows

- **Dashboard Development**: `.agent/workflows/dashboard-workflow.md`
- **Primary Workflow**: `.claude/workflows/primary-workflow.md`
- **Dev Rules**: `.claude/workflows/development-rules.md`

## 📝 Code Style Guidelines

- **Frontend**:
  - Use **TypeScript** for all components.
  - Use **Tailwind CSS** for styling (avoid inline styles).
  - Components must have **JSDoc** and **ARIA labels**.
  - Follow the **Semantic Color Scheme** defined in `README.md`.
- **Backend**:
  - Follow **PEP 8** standards.
  - Use Type Hints.
  - Document API endpoints.

## 🚀 Deployment Checklist

1. **Build Frontend**: Ensure `npm run build` passes without errors.
2. **Verify Backend**: Ensure API is responding at `http://localhost:8000`.
3. **Check Environment**: Verify `.env` and `.env.local` are configured.
4. **Test UI**: Verify Dashboard rendering and Chart interactivity.

---
*Updated to Claude Engineer Kit v2.0 Standards*