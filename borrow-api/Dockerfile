FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# ---- test stage: run by Jenkins with `docker build --target test` ----
FROM base AS test
RUN pip install --no-cache-dir pytest==8.3.3 ruff==0.7.0 \
 && ruff check . \
 && pytest -q

# ---- production stage ----
FROM base AS production
RUN useradd --create-home appuser
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:create_app()"]
