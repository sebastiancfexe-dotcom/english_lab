# English Lab

App en Django para practicar inglés: vocabulario por niveles, verbos, inglés para desarrolladores, dictado de frases y práctica oral.

## Con Docker (recomendado para moverlo a otro equipo)

Necesitas Docker con Compose. En Windows, Docker Desktop requiere WSL 2 (`wsl --install` en una terminal de administrador, y reiniciar).

```bash
cp .env.example .env        # en PowerShell: Copy-Item .env.example .env
# Edita .env y define DJANGO_SECRET_KEY (ahí mismo hay un comando para generarla)
docker compose up -d --build
```

Abre http://localhost:8000. En el primer arranque se cargan las palabras, verbos, frases y preguntas.

Crear un administrador (para `/admin`):

```bash
docker compose exec web python manage.py createsuperuser
```

Comandos útiles:

```bash
docker compose logs -f web      # ver el log
docker compose down             # apagar (los datos se conservan)
docker compose up -d --build    # aplicar cambios del código
docker compose down -v          # apagar y BORRAR los datos
```

### Dónde quedan los datos
La base de datos SQLite vive en el volumen `english_lab_english_data` (dentro del contenedor, `/data/db.sqlite3`), así que sobrevive a reinicios y reconstrucciones.

Copia de seguridad:

```bash
docker compose cp web:/data/db.sqlite3 ./copia-db.sqlite3
```

Llevar tu base de datos local a Docker (progreso y usuarios incluidos), con el contenedor ya levantado una vez:

```bash
docker compose cp ./db.sqlite3 web:/data/db.sqlite3
docker compose restart web
```

### Si lo publicas en un servidor
- Pon el dominio en `DJANGO_ALLOWED_HOSTS` y `DJANGO_CSRF_TRUSTED_ORIGINS` (con `https://`).
- Usa HTTPS delante (Caddy, nginx o el proxy de tu proveedor). Sin HTTPS las contraseñas viajan en claro.
- Usa una `DJANGO_SECRET_KEY` propia y larga.

## Sin Docker (desarrollo)

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py cargar_datos
.venv\Scripts\python.exe manage.py createsuperuser
.venv\Scripts\python.exe manage.py runserver
```

Pruebas: `.venv\Scripts\python.exe manage.py test practica`

## Contenido
`cargar_datos` carga o actualiza el contenido y se puede repetir sin duplicar, pero **pisa las traducciones y ejemplos que hayas editado en el admin**. Con `--si-vacio` solo carga si la base está vacía (así lo usa Docker al arrancar).
