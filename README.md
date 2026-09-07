# Password Manager Backend

Backend API for a client-server password manager built with FastAPI.
Provides user authentication, JWT access/refresh tokens, role-based access, encrypted vaults, and backup management.

## Features
- User registration and login
- JWT authentication with access (bearer) and refresh tokens
- Session management with logout
- Password change endpoint
- **Vaults**: create, rename, delete, pin/unpin, unlock with master password
- **Encrypted password entries**: add, get, delete, update passwords inside vaults (AES Fernet, DEK encrypted with master password)
- Backup vault: upload, download, rename, delete, pin/unpin
- Prometheus-compatible `/metrics` endpoint (admin-only)
- Health check at `/health`
- Role-based access (user/admin)
- PostgreSQL database with Alembic migrations
- Docker-based local setup
- Telegram bot integration (work in progress)
- API tests with pytest (55 tests)

## Tech Stack
- Python — FastAPI, SQLAlchemy (async), Alembic, cryptography
- PostgreSQL
- Docker / Docker Compose
- pytest

## Project Structure
```
alembic/               — Alembic migrations
nginx/                 — Nginx configuration
scripts/               — Entrypoint and helper scripts
backend/
  bot/                 — Telegram bot (work in progress)
  core/                — Settings, DB, logging
  dao/                 — Data Access Objects
  dependencies.py      — Dependency injection (auth, validation)
  exceptions/          — Custom exception handlers
  metrics/             — Middleware, router, storage (request metrics)
  models/              — SQLAlchemy ORM models
  password_manager/    — Password crypto, schemas, password tool
    core/              — Crypto logic, directories
    schemas/           — Pydantic schemas for passwords
  routers/
    api/               — JSON API endpoints (auth, backups, stats)
    web/               — Web UI endpoints (vaults, passwords, users, backups)
  schemas/             — Shared Pydantic schemas
  services/            — Business logic (JWT, backup, secrets, cookies)
tests/                 — pytest test suite (unit, integration, api)
PASSWORDS_DATA/        — Exported passwords, vaults, imports (gitignored)
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

## API Endpoints (prefix: `/api`)

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
| POST | `/backups/upload` | Bearer | Upload a new backup |
| GET | `/backups` | Bearer | List user's backups |
| POST | `/backups/download` | Bearer | Download a backup by ID |
| DELETE | `/backups/{backup_id}` | Bearer | Delete a backup |
| PATCH | `/backups/{backup_id}` | Bearer | Rename a backup |
| PATCH | `/backups/{backup_id}/change-pin` | Bearer | Toggle pin on a backup |

### Stats
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/backups/stats` | Admin | Backup statistics |

## Web Endpoints (prefix: `/web`)

### Users
| Method | Path | Description |
|--------|------|-------------|
| POST | `/login` | Login with redirect |
| POST | `/logout` | Logout |
| GET | `/refresh` | Refresh tokens |
| POST | `/change-password` | Change password |
| GET | `/me` | Current user info |

### Backups
| Method | Path | Description |
|--------|------|-------------|
| POST | `/backups/upload` | Upload a backup |
| GET | `/backups` | List backups |
| GET | `/backups/{backup_id}` | Get backup details |
| POST | `/backups/{backup_id}/download` | Download backup |
| DELETE | `/backups/{backup_id}` | Delete backup |
| PATCH | `/backups/{backup_id}` | Rename backup |
| PATCH | `/backups/{backup_id}/change-pin` | Toggle pin |

### Vaults
| Method | Path | Description |
|--------|------|-------------|
| POST | `/vaults/create` | Create new vault |
| DELETE | `/vaults/{vault_id}` | Delete vault |
| POST | `/vaults/{vault_id}/rename` | Rename vault |
| GET | `/vaults` | List user's vaults |
| POST | `/vaults/{vault_id}/unlock` | Unlock vault with master password |
| POST | `/vaults/{vault_id}/status` | Get vault status (locked/unlocked) |
| GET | `/vaults/{vault_id}/info` | Vault metadata |
| POST | `/vaults/{vault_id}/change-pin` | Toggle vault pin |
| POST | `/vaults/{vault_id}/download` | Download vault as encrypted backup |

### Passwords (inside vault)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/vaults/{vault_id}/passwords/add` | Add password entry |
| POST | `/vaults/{vault_id}/passwords/get` | Get all password entries |
| POST | `/vaults/{vault_id}/passwords/delete` | Delete password entry |
| POST | `/vaults/{vault_id}/passwords/update` | Update password entry |

## System Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Health check |
| GET | `/metrics` | Admin | Request metrics (count, active, duration) |
