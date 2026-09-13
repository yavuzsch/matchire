# Matchire
An AI-assisted recruitment platform. Candidates get a live compatibility score against job listings and take an AI-generated skills assessment if selected. Employers create listings, rank candidates, and manage the hiring pipeline.

## Tech stack
**Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL (Supabase), JWT auth, Google Gemini.
**Frontend:** React 19, Vite, React Router, Tailwind CSS 4. Bilingual (TR/EN).


## Structure
```
backend/app/
├── core/  # settings, db session, auth dependencies, error codes
├── models/  # SQLAlchemy database models
├── schemas/  # Pydantic request/response schemas
├── routers/  # API endpoints, grouped by resource
├── services/  # matching logic, LLM parsing, and evaluation
└── prompts/  # LLM prompt templates
 
frontend/src/
├── pages/  # route-level screens, grouped by role
├── components/  # reusable UI pieces (layout, forms, badges)
├── i18n/  # translations
└── api/client.js  # fetch wrapper with auth and error handling
```


## Setup
**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL, SECRET_KEY, LLM_API_KEY
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```
→ `http://localhost:8001` (docs at `/docs`)

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_URL
npm run dev
```
→ `http://localhost:5173`

**Tests**
```bash
cd backend && pytest
```
Schema is built from the models directly, independent of Alembic.


## Environment variables
| Backend | | Frontend | |
|---|---|---|---|
| `DATABASE_URL` | Postgres connection string | `VITE_API_URL` | Backend base URL |
| `SECRET_KEY` | JWT signing secret | | |
| `LLM_API_KEY` | Gemini API key | | |
| `LLM_PROVIDER` | default `gemini` | | |
| `LLM_MODEL` | Gemini model name | | |
| `CORS_ORIGINS` | allowed frontend origins | | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry | | |
| `DEFAULT_LANGUAGE` | LLM prompt language (`tr`/`en`) | | |


## Notes
- i18n keys live in `frontend/src/i18n/tr.js` and `en.js` — add new keys to both, no fallback.
- Auth is a JWT in `localStorage`; assessment answers are drafted there too, so they survive a reload.