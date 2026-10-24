FROM ghcr.io/astral-sh/uv:python3.14-alpine

COPY pyproject.toml uv.lock /app/

WORKDIR /app

RUN uv sync --locked --no-dev

COPY src/ /app/src

WORKDIR /app/src

CMD [ "uv", "run", "volobot.py" ]
