#!/bin/bash


./.venv/bin/alembic upgrade head
echo Alembic upgrade head successful

# ./.venv/bin/python scripts/nginx_configure.py
# echo Nginx Configured

./.venv/bin/uvicorn src.main:app --port 8000 --host 0.0.0.0 --forwarded-allow-ips="*"
echo API server started


