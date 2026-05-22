# Password Manager Backend

Backend API for a client-server password manager built with FastAPI.
It provides user authentication, JWT access/refresh tokens, and backup vault management.

## Features
- User registration and login
- JWT authentication with access and refresh tokens
- Backup vault upload, download and delete
- PostgreSQL database with Alembic migrations
- Docker-based local setup
- API tests with pytest

## Tech Stack
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker / Docker Compose
- pytest

## Project Structure
- alembic — Настройка Alembic
- nginx — Настройка Nginx
- scripts - Скрипты для entrypoint и не только
- src/api — Роуты
- src/services — Бизнес-логика
- src/models — ORM модели
- src/schemas — Pydantic схемы
- src/core — Конфиг, безопасность, БД
- src/bot - Заготовка под бота в тг
- tests — Тесты

## Environment Variables
```#API & DB
DB_HOST=db
DB_PORT=5432
DB_NAME=app_db
DB_USER=app_user
DB_PASSWORD=secret

#JWT
SECRET_TOKEN_KEY=SECRET_TOKEN_KEY

#BOT
BOT_TOKEN=TOKEN

#NGINX
SERVER_NAME=localhost
PROXY_PASS=http://api:8000
```

## API Endpoints
POST     /register

POST     /login

GET      /refresh

GET      /backups

POST     /backups/upload

POST     /backups/download

DELETE   /backups/{id}
