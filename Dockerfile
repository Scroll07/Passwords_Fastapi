FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

COPY uv.lock pyproject.toml ./

RUN uv sync --frozen --no-dev --no-cache

COPY . .

RUN chmod +x ./start.sh

EXPOSE 8000

CMD ["./start.sh"]



