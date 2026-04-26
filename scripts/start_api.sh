#!/bin/bash

echo API server started

./.venv/bin/alembic upgrade head
./.venv/bin/uvicorn src.main:app --port 8000 --host 0.0.0.0 --forwarded-allow-ips="*"


