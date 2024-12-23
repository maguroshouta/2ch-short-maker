FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

WORKDIR /app

RUN apt update && apt install -y wget gpg unzip

RUN dpkg --add-architecture i386 && \
  mkdir -pm755 /etc/apt/keyrings && \
  wget -O - https://dl.winehq.org/wine-builds/winehq.key | gpg --dearmor -o /etc/apt/keyrings/winehq-archive.key - && \
  wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/debian/dists/bookworm/winehq-bookworm.sources

RUN apt update && apt install -y --install-recommends winehq-stable ffmpeg

RUN wget https://www.a-quest.com/archive/package/aquestalkplayer_20241104.zip && \
  mkdir -p /app/backend/static/aquestalk/ && \
  unzip aquestalkplayer_20241104.zip -d /app/backend/static/aquestalk/ && \
  rm aquestalkplayer_20241104.zip

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project --no-dev

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT []

CMD ["fastapi", "run", "app/main.py", "--port", "3000"]