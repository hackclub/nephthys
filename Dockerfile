FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN apt-get update
RUN apt-get install -y curl libatomic1

RUN uv python install
RUN uv sync --frozen

EXPOSE 3000

ENV PATH="/app/.venv/bin:$PATH"

CMD ["./entrypoint.sh"]

HEALTHCHECK --start-period=5s CMD curl --fail http://localhost:3000/health | grep -E '"healthy":\s*true' || exit 1
