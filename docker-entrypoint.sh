#!/bin/sh
set -e

python manage.py migrate --noinput

# Solo carga el contenido la primera vez (base vacía), para no pisar lo que edites en el admin.
python manage.py cargar_datos --si-vacio

# Usuario administrador opcional: define DJANGO_SUPERUSER_USERNAME y DJANGO_SUPERUSER_PASSWORD en .env
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py createsuperuser --noinput \
        || echo "Aviso: no se creó el superusuario (probablemente ya existe)."
fi

exec "$@"
