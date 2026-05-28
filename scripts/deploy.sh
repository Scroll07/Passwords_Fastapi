#!/bin/bash

set -e

PROJECT_DIR="/home/vlad/projects/Passwords_Fastapi"
BRANCH="main"

cd "$PROJECT_DIR"

git fetch

git checkout "$BRANCH"

git pull origin "$BRANCH"

docker compose up -d --build
