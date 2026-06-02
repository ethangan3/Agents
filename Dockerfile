FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* README.md ./
COPY src ./src
COPY frontend ./frontend
COPY demos ./demos
COPY docs ./docs
COPY .env.example ./.env.example

RUN uv sync --locked --no-dev --extra frontend

EXPOSE 8000 8501

CMD ["uvicorn", "mini_agent.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
