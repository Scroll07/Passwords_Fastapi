# Password Manager Backend

Backend API for a client-server password manager built with FastAPI.
It provides user authentication, JWT access/refresh tokens, role-based access, and backup vault management.

## Features
- User registration and login
- JWT authentication with access (bearer) and refresh tokens
- Session management with logout
- Password change endpoint
- Backup vault: upload, download, rename, delete
- Pin/unpin backups
- Prometheus-compatible `/metrics` endpoint (admin-only)
- Health check at `/health`
- Role-based access (user/admin)
- PostgreSQL database with Alembic migrations
- Docker-based local setup
- API tests with pytest (32 tests)

## Tech Stack
- Python — FastAPI, SQLAlchemy (async), Alembic
- PostgreSQL
- Docker / Docker Compose
- pytest

## Project Structure
```
alembic/              — Alembic migrations
nginx/                — Nginx configuration
scripts/              — Entrypoint and helper scripts
src/
  api/                — API routers (users, passwords/backups)
  bot/                — Telegram bot (work in progress)
  core/                — Settings, DB, logging, templates
  dao/                 — Data Access Objects
  dependencies.py      — Dependency injection (auth, validation)
  exceptions/          — Custom exception handlers
  metrics/             — Middleware, router, storage (request metrics)
  models/              — SQLAlchemy ORM models
  routers/
    api/               — JSON API endpoints
    web/                — Web UI endpoints
  schemas/             — Pydantic schemas
  services/            — Business logic (JWT, backup, secrets)
tests/                 — pytest test suite
BACKUPS_DATA/          — Uploaded backup files (gitignored)
```

## Environment Variables
```bash
# API & DB
DB_HOST=db
DB_PORT=5432
DB_NAME=app_db
DB_USER=app_user
DB_PASSWORD=secret

# JWT
SECRET_TOKEN_KEY=SECRET_TOKEN_KEY

# App mode & admin credentials
APP_MODE=development
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

# Bot (optional)
BOT_TOKEN=TOKEN

# Nginx (optional)
SERVER_NAME=localhost
PROXY_PASS=http://api:8000
```

## API Endpoints

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | — | Register new user |
| POST | `/login` | — | Login, returns bearer + refresh tokens |
| POST | `/logout` | Bearer | Invalidate current session |
| GET | `/refresh` | Refresh | Refresh both tokens |
| PATCH | `/change-password` | Bearer | Change account password |

### Backups
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/backups` | Bearer | List user's backups |
| POST | `/backups/upload` | Bearer | Upload a new backup |
| POST | `/backups/download` | Bearer | Download a backup by ID |
| DELETE | `/backups/{id}` | Bearer | Delete a backup |
| PATCH | `/backups/{id}` | Bearer | Rename a backup |
| PATCH | `/backups/{id}/change-pin` | Bearer | Toggle pin on a backup |

### System
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Health check |
| GET | `/metrics` | Admin | Request metrics (count, active, duration) |
