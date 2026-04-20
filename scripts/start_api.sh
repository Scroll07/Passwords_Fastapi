#!/bin/bash

echo API server started

uv run alembic upgrade head
uv run uvicorn src.main:app --port 8000 --host 0.0.0.0 --forwarded-allow-ips="*"


