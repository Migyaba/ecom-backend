FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN useradd --system --uid 1000 --home /app django

COPY --chown=django:django . .

# Fichiers statiques compilés dans l'image (servis par WhiteNoise).
# Les valeurs factices ne servent qu'à charger les settings pendant le build.
RUN SECRET_KEY=collectstatic-only ALLOWED_HOSTS=localhost python manage.py collectstatic --noinput \
    && chown -R django:django /app/staticfiles \
    && chmod +x /app/docker/entrypoint.sh

USER django

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python /app/docker/healthcheck.py

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "--forwarded-allow-ips", "*"]
