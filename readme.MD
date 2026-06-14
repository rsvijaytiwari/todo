# Todos API

A production-ready async REST API built with **FastAPI**, **SQLAlchemy 2.0 ORM**, and **asyncpg**, connected to a NeonDB PostgreSQL database. The project follows a clean layered architecture: router → endpoint → service → repository → database.

---

## Project structure

```
todos_app/
├── app/
│   ├── main.py                        # App factory, lifespan handler
│   ├── core/
│   │   └── config.py                  # Settings via pydantic-settings + .env
│   ├── db/
│   │   ├── base.py                    # DeclarativeBase
│   │   ├── session.py                 # Async engine + session factory
│   │   └── deps.py                    # get_db() FastAPI dependency
│   ├── models/
│   │   └── todo.py                    # Todo + Category ORM models
│   ├── schemas/
│   │   └── todo.py                    # Pydantic request + response schemas
│   ├── repositories/
│   │   └── todo_repository.py         # All DB queries (ORM only, no raw SQL)
│   ├── services/
│   │   └── todo_service.py            # Business logic, HTTP error handling
│   └── api/
│       └── v1/
│           ├── router.py              # Aggregates all v1 routers
│           └── endpoints/
│               └── todos.py           # Thin endpoint handlers
├── .env.example
└── requirements.txt
```

---

## Request flow
![Project Screenshot](./request-flow.svg)
```
Client
  │  HTTP request
  ▼
Uvicorn (ASGI)
  │  parses HTTP, calls ASGI app
  ▼
APIRouter  ──── matches path + method
  │
  ├── get_db() ──── opens AsyncSession (injected as dependency)
  │
  ▼
Endpoint handler  ──── validates Pydantic schema
  │
  ▼
TodoService  ──── business logic, raises HTTPException on error
  │
  ▼
TodoRepository  ──── ORM queries (select / insert / update / delete)
  │
  ▼
PostgreSQL / NeonDB  ──── asyncpg connection pool
  │
  ▼  (response travels back up through the same layers)
Client  ◄──── JSON response
```

The `get_db()` dependency manages the session lifecycle: it commits on success and rolls back automatically on any exception — the endpoint and service layers never touch the session directly.

---

## Setup

**1. Clone and install dependencies**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname?ssl=require
APP_ENV=development
DEBUG=true
```

**3. Run the server**

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs` (development only).

---

## API reference

All endpoints are prefixed with `/v1/todos`.

### Create a todo

```
POST /v1/todos
```

Request body:

```json
{
  "task_name": "Book flights",
  "category_id": 2,
  "description": "Check Skyscanner for options",
  "deadline": "2025-08-01T00:00:00"
}
```

### List todos

```
GET /v1/todos
GET /v1/todos?category_id=2
```

### Get a single todo

```
GET /v1/todos/{todo_id}
```

### Update a todo (partial)

```
PATCH /v1/todos/{todo_id}
```

Only the fields provided in the body are updated. Sending an empty body returns `400`.

### Delete a todo

```
DELETE /v1/todos/{todo_id}
```

---

## Response format

All endpoints return a consistent envelope:

```json
{
  "message": "success",
  "data": { ... }
}
```

Errors follow FastAPI's standard format:

```json
{
  "detail": "Todo 42 not found"
}
```

---

## Architecture decisions

**Repository pattern** — all database access is encapsulated in `TodoRepository`. The service layer never imports SQLAlchemy directly, which makes it straightforward to swap the data source or add caching later.

**`exclude_unset=True` in PATCH** — only fields explicitly provided in the request body are applied to the ORM model. This prevents `null` from silently overwriting existing values when a field is omitted.

**Session lifecycle in `get_db()`** — the dependency commits after the endpoint returns and rolls back on any exception. No manual transaction management is needed inside services or repositories.

**ORM with `joinedload`** — the `category_name` field on `TodoResponse` is populated via a joined load on `Todo.category`, avoiding N+1 queries on list endpoints.

**Docs hidden in production** — `/docs` and `/redoc` are only mounted when `APP_ENV=development`, controlled via the app factory in `main.py`.

---

## Database schema

```sql
CREATE TABLE categories (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE todos (
    id          SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    task_name   VARCHAR(255) NOT NULL,
    description TEXT,
    deadline    TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## Environment variables

| Variable       | Required | Default       | Description                          |
|----------------|----------|---------------|--------------------------------------|
| `DATABASE_URL` | Yes      | —             | asyncpg-compatible PostgreSQL URL    |
| `APP_ENV`      | No       | `development` | Set to `production` to hide API docs |
| `DEBUG`        | No       | `false`       | Enables SQLAlchemy query logging     |

---

## Tech stack

| Layer        | Library                        |
|--------------|--------------------------------|
| Web framework | FastAPI                       |
| ASGI server  | Uvicorn                        |
| ORM          | SQLAlchemy 2.0 (async)         |
| DB driver    | asyncpg                        |
| Validation   | Pydantic v2                    |
| Config       | pydantic-settings              |
| Database     | PostgreSQL (NeonDB)            |