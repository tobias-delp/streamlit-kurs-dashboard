
FROM ghcr.io/astral-sh/uv:python3.14-alpine

# Python- und uv-Konfiguration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_DEV=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Abhängigkeiten separat installieren (Docker Cache)
COPY pyproject.toml uv.lock README.md ./
COPY src/streamlit_kurs_dashboard/__init__.py \
     src/streamlit_kurs_dashboard/__init__.py

RUN uv sync --locked --no-dev --no-install-project

# Anwendung und Daten kopieren
COPY src/ ./src/
COPY data/ ./data/

# Projekt installieren
RUN uv sync --locked --no-dev

# Benutzer ohne Root-Rechte
RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup && \
    chown -R appuser:appgroup /app

USER appuser

# Streamlit-Port
EXPOSE 8501

# Streamlit starten
CMD ["streamlit", "run", \
     "src/streamlit_kurs_dashboard/app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true"]
