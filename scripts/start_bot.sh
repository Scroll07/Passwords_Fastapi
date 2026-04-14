#!/bin/bash

echo Telegram bot started

export PYTHONPATH=/app:PYTHONPATH

exec /app/.venv/bin/python /app/src/bot/main.py