# freelance_service — Contratación de freelancers (MVP)

Microservicio Flask de Desk Colaborador para **publicar un proyecto, recibir propuestas de
freelancers, compararlas y contratar**. Incluye frontend (HTML server-side, tema oscuro de
Desk) y API REST JSON. Requisitos y criterios de aceptación: [SPEC.md](SPEC.md).

## Arranque rápido (local)

Desde la raíz del repo:

```bash
pip install -r requirements.txt                      # o usa .venv/
FREELANCE_SEED_DEMO=1 python freelance_service/run.py   # http://localhost:5002
```

Producción / staging (gunicorn):

```bash
FREELANCE_DATABASE_URL=sqlite:////ruta/persistente/freelance.db \
FREELANCE_SECRET_KEY=<aleatorio> \
gunicorn freelance_service.wsgi:app -b 0.0.0.0:8002
```

Docker: `docker-compose up -d --build freelance` (puerto 8002, datos en el volumen `freelance-data`).

### Variables de entorno

| Variable | Por defecto | Uso |
|---|---|---|
| `FREELANCE_DATABASE_URL` | `sqlite:///<instance>/freelance.db` | Base de datos (SQLAlchemy URL). |
| `FREELANCE_SECRET_KEY` | `dev` | Firma de la sesión (mensajes flash). Cámbiala en staging/prod. |
| `FREELANCE_SEED_DEMO` | — | `1` carga datos de ejemplo si la BD está vacía. |
| `FREELANCE_CHANGE_REQUEST_URL` | — | Enlace «Solicitar cambios» del pie de página. |

Comandos CLI: `flask --app freelance_service seed-demo` y `flask --app freelance_service reset-db`.

## Uso (frontend)

1. **Nuevo proyecto** → rellena título, descripción, habilidades (`python, flask`), presupuesto y fecha límite.
2. En la ficha del proyecto copia el **enlace para freelancers** (`/projects/<id>/apply`) y compártelo.
3. Las propuestas aparecen ordenadas por **encaje de habilidades**, ajuste al presupuesto y precio.
4. **Preseleccionar / Rechazar / Contratar**. Al contratar se crea el contrato y el resto de propuestas se rechaza.
5. En **Contratos** marca el trabajo como **finalizado** al terminar (cierra el proyecto).

## API REST

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/api/stats` | KPIs |
| GET/POST | `/api/projects` | Listar (`?status=abierto`) / crear proyecto |
| GET | `/api/projects/<id>` | Detalle con propuestas ordenadas y contrato |
| POST | `/api/projects/<id>/close` | Cerrar sin contratar |
| GET/POST | `/api/projects/<id>/proposals` | Listar ordenadas / enviar propuesta |
| PATCH | `/api/proposals/<id>` | `{"status": "pendiente"\|"preseleccionada"\|"rechazada"}` |
| POST | `/api/proposals/<id>/hire` | Contratar → crea contrato |
| GET | `/api/contracts` | Listar contratos |
| POST | `/api/contracts/<id>/complete` | Finalizar contrato |
| GET | `/api/freelancers` | Listar freelancers |

Errores: JSON `{"error": "..."}` con 400 (validación), 404 (no existe) o 409 (estado no permite la acción).

Ejemplo de flujo completo con `curl`:

```bash
B=http://localhost:8002
curl -s -XPOST $B/api/projects -H 'Content-Type: application/json' \
  -d '{"title":"MVP","description":"Portal","skills":"python,flask","budget_max":5000}'
curl -s -XPOST $B/api/projects/1/proposals -H 'Content-Type: application/json' \
  -d '{"name":"Ana","email":"ana@example.com","skills":"python,flask","amount":4000,"days":30,"message":"Hola"}'
curl -s $B/api/projects/1/proposals          # ranking
curl -s -XPOST $B/api/proposals/1/hire       # contrato creado
```

## Tests

```bash
python -m pytest test_freelance.py -v
```
