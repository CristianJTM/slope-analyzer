# Docker + CI — Especificación

Empaquetar backend + frontend con Docker Compose y validar en CI.

## Servicios

- **backend**: Python 3.12 + uvicorn en `:8000`. SQLite en el volumen `db-data`
  (`DATABASE_URL=sqlite:////app/data/slope.db`).
- **frontend**: build de Vite + nginx en `:80`, publicado en el host como
  `:8080`. nginx sirve la SPA y proxea `/api/` a `backend:8000`.

Con el proxy de nginx, el frontend usa `/api/v1` relativo (mismo origen), así
que no depende de CORS. En desarrollo, Vite hace el mismo proxy a
`http://127.0.0.1:8000`.

## Uso

```powershell
docker compose up --build
```

- Frontend: `http://localhost:8080`
- API / Swagger: `http://localhost:8000/docs`

```powershell
docker compose down          # detiene
docker compose down -v       # detiene y borra el volumen (historial)
```

## CI (`.github/workflows/ci.yml`)

- **backend**: instala requirements y corre `pytest`.
- **frontend**: `npm ci` + `npm run build`.
- **docker**: `docker compose build` (valida los Dockerfiles).

Se dispara en `push` a `main` y en `pull_request`.

## Fuera de alcance

Registry de imágenes, despliegue y migraciones Alembic.
