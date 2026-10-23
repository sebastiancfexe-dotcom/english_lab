FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias primero: se cachea mientras requirements.txt no cambie.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Usuario sin privilegios; /data guarda la base de datos SQLite (volumen).
RUN useradd --create-home app \
    && mkdir /data \
    && chown app:app /data \
    && sed -i 's/\r$//' docker-entrypoint.sh \
    && chmod +x docker-entrypoint.sh \
    && DJANGO_DEBUG=0 DJANGO_SECRET_KEY=solo-para-el-build python manage.py collectstatic --noinput

USER app
ENV DJANGO_DEBUG=0 \
    DJANGO_DB_PATH=/data/db.sqlite3
VOLUME /data
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/cuentas/entrar/', timeout=4)"

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
