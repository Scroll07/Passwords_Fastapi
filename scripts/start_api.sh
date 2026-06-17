#!/bin/bash


echo Alembic upgrade
./.venv/bin/alembic upgrade head

# ./.venv/bin/python scripts/nginx_configure.py
# echo Nginx Configured

echo API server start
./.venv/bin/uvicorn main:app --port 8000 --host 0.0.0.0 --forwarded-allow-ips="*"


