# Frontend de English Lab

React + Vite. Habla con el API de Django mediante JWT.

```bash
cp .env.example .env.local      # VITE_API_URL=http://localhost:8000
npm install
npm run dev                     # http://localhost:5173
npm run build                   # genera dist/ para publicar como sitio estático
npm run lint
```

`VITE_API_URL` se incorpora al compilar: si cambia, hay que volver a construir.

- `src/api.js`: cliente del API (tokens JWT y renovación automática).
- `src/auth.jsx`: sesión del usuario.
- `src/components/`: layout con barra lateral, gráficas en SVG y utilidades.
- `src/pages/`: una pantalla por ruta.
