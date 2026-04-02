FROM ghcr.io/astral-sh/uv:python3.14-alpine

RUN addgroup -g 1000 flaskblog && \
    adduser -u 1000 -G flaskblog -D flaskblog

WORKDIR /app

RUN chown flaskblog:flaskblog /app

USER flaskblog

COPY --chown=flaskblog:flaskblog app/pyproject.toml app/uv.lock ./

RUN uv sync --frozen --no-dev --no-cache && \
    find .venv -type d -name tests -exec rm -rf {} + 2>/dev/null; true

COPY --chown=flaskblog:flaskblog app/ .

RUN mkdir -p instance log

ENV PYTHONUNBUFFERED=1
ENV APP_HOST=0.0.0.0
ENV APP_PORT=1283

EXPOSE 1283

CMD ["uv", "run", "gunicorn", "-w", "4", "-b 0.0.0.0", "app:app"]
