# Sentinel Health — bundled container for Cloud Run (FastAPI + Ollama + Gemma 4)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    OLLAMA_HOST=0.0.0.0:11434 \
    OLLAMA_MODELS=/root/.ollama/models

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates procps \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Bake the model into the image so Cloud Run cold starts don't pay a ~10 GB pull.
# Ollama needs the daemon up to pull; start it, pull, then stop.
RUN ollama serve & \
    OLLAMA_PID=$! && \
    until curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; do sleep 1; done && \
    ollama pull gemma4:e4b-it-q4_K_M && \
    kill $OLLAMA_PID && wait $OLLAMA_PID 2>/dev/null || true

COPY app/ ./app/
COPY demo/ ./demo/
COPY main.py ./
COPY scripts/start.sh /start.sh
RUN chmod +x /start.sh

ENV PORT=8080
EXPOSE 8080

CMD ["/start.sh"]
