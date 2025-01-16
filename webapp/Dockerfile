FROM python:3.10-slim-bullseye AS base

# RUN export DEBIAN_FRONTEND=noninteractive
# RUN --mount=type=cache,id=cdc-demo-webapp-base-install,target=/var/cache/apt apt-get update -yq && \
#     apt-get install -yq --no-install-recommends ffmpeg libsm6 libxext6 curl && \
#     rm -rf /var/lib/apt/lists/*

# https://github.com/orgs/python-poetry/discussions/1879#discussioncomment-216865
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # uv
    # Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
    UV_COMPILE_BYTECODE=1 \
    # Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
    UV_LINK_MODE=copy \
    UV_PYTHON=3.10 \
    # UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

FROM base AS builder

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.5.10 /uv /uvx /bin/

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,id=cdc-demo-webapp-uv-install,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY alembic.ini /app
COPY ./app /app/app

RUN --mount=type=cache,id=cdc-demo-webapp-uv-install,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev

FROM base AS runtime

COPY ./scripts/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY ./scripts/prestart.sh /prestart.sh
RUN chmod +x /prestart.sh

COPY ./scripts/start.sh /start.sh
RUN chmod +x /start.sh

COPY --from=builder /app/ /app/
