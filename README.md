# English Lab

App para practicar inglés: vocabulario por niveles, verbos, inglés para desarrolladores, dictado de frases y práctica oral.

| Pieza | Tecnología | Dónde vive |
|---|---|---|
| Frontend | React + Vite (`frontend/`) | Sitio estático en Render |
| Backend | Django + Django REST Framework, solo API (`api/`) y `/admin` | Servicio Docker en Render |
| Base de datos | PostgreSQL | Supabase (plan gratuito) |

El navegador habla solo con el API de Django (login con JWT). Supabase se usa únicamente como Postgres alojado.

## Puesta en marcha en local

Necesitas Python 3.13 y Node.js 24.

1. **Base de datos.** Crea un proyecto en [supabase.com](https://supabase.com) y copia la cadena de conexión
   *Connect → Session pooler*. Usa una contraseña de solo letras y números.
2. **Variables de entorno.**

   ```bash
   cp .env.example .env        # en PowerShell: Copy-Item .env.example .env
   ```

   Edita `.env`: define `DJANGO_SECRET_KEY` (el comando para generarla está en el archivo) y `DATABASE_URL`.
   Sin `DATABASE_URL` el backend usa SQLite local.
3. **Backend.**

   ```bash
   python -m venv .venv && .venv/Scripts/activate      # Linux/Mac: source .venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py cargar_datos      # vocabulario, verbos, frases y preguntas orales (puede tardar unos minutos sobre Supabase)
   python manage.py runserver 8000
   ```

4. **Frontend.**

   ```bash
   cd frontend
   cp .env.example .env.local         # VITE_API_URL=http://localhost:8000
   npm install
   npm run dev
   ```

Abre http://localhost:5173 y crea tu cuenta. Un administrador para `/admin`: `python manage.py createsuperuser`.

## Con Docker

```bash
cp .env.example .env                 # y completa DJANGO_SECRET_KEY y DATABASE_URL
docker compose up -d --build
```

- API: http://localhost:8000 (healthcheck en `/api/salud/`, admin en `/admin/`)
- Frontend (Vite): http://localhost:5173

```bash
docker compose logs -f api           # ver el log
docker compose down                  # apagar (los datos viven en Supabase, no en el contenedor)
```

## Despliegue en Render

El archivo `render.yaml` define las dos piezas (plan gratuito).

1. Sube el repositorio a GitHub.
2. En Render: **New → Blueprint** y elige el repositorio. Crea `english-lab-api` y `english-lab`.
3. Cuando lo pida, completa las variables marcadas como secretas:
   - `english-lab-api`: `DATABASE_URL` (Session pooler de Supabase), `DJANGO_CORS_ALLOWED_ORIGINS` y
     `DJANGO_CSRF_TRUSTED_ORIGINS` con la URL del sitio estático (por ejemplo `https://english-lab.onrender.com`).
   - `english-lab`: `VITE_API_URL` con la URL del API (por ejemplo `https://english-lab-api.onrender.com`).
4. Si las URLs reales difieren de las supuestas, corrige esas variables y redespliega el sitio estático
   (`VITE_API_URL` se incorpora al compilar).

Límites del plan gratuito: el API se duerme tras unos 15 minutos sin tráfico y la primera petición tarda cerca de un
minuto en despertarlo; Supabase pausa el proyecto tras una semana sin actividad.

## Tests

```bash
DATABASE_URL=sqlite:///:memory: python manage.py test      # PowerShell: $env:DATABASE_URL='sqlite:///:memory:'
```

Corren contra SQLite en memoria para no crear bases de datos de prueba en Supabase.

## Estructura

- `api/`: endpoints JSON, JWT y tests de la API.
- `practica/`, `vocabulario/`, `verbos/`, `usuarios/`: modelos y lógica (`practica/servicios.py` concentra el test de
  nivel, el dominio de palabras, la selección de ejercicios y las estadísticas).
- `frontend/`: la app React.
