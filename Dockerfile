FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY server/ server/
COPY pyproject.toml uv.lock* ./

RUN uv sync --package smello-server --no-dev --frozen

EXPOSE 5110

ENV SMELLO_DB_PATH=/data/smello.db

CMD ["uv", "run", "--package", "smello-server", "smello-server", "run"]
