# Migrating from FastAPI to py-cheema-api

py-cheema-api mirrors FastAPI's ergonomics closely enough that most projects
migrate in under an hour, with no compiled toolchain, no Zig, and no
free-threaded Python requirement. This guide covers what's a drop-in swap,
what needs a small adjustment, and what doesn't map over yet.

## Step 1: Swap the imports

```python
# Before
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

# After — stdlib-only path (no Pydantic dependency)
from cheema import Cheema as FastAPI, Depends, HTTPException
from cheema import Model as BaseModel, field
```

If you'd rather the import path match the `pip install py-cheema-api`
package name exactly, `py_cheema_api` is available as an alias for the same
package:

```python
from py_cheema_api import Cheema as FastAPI, Depends, HTTPException
from py_cheema_api import Model as BaseModel, field
```

If you want to keep using Pydantic v2 models unchanged during migration:

```bash
pip install "py-cheema-api[pydantic]"
```

```python
from cheema import Cheema as FastAPI, Depends, HTTPException
from pydantic import BaseModel  # keep as-is, still supported
```

This lets you migrate route-by-route without rewriting every model on day one.

## Step 2: Run it

```python
# FastAPI way (still works — py-cheema-api is a real ASGI app)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

No second "native runtime" step required — unlike frameworks with a compiled
core, there's no `app.run()` fast-path you're leaving performance on the
table by skipping. uvicorn *is* the intended production path here.

## Compatibility matrix

| Feature | FastAPI | py-cheema-api | Notes |
|---|---|---|---|
| Route decorators (`@app.get`, etc.) | ✅ | ✅ | Direct match |
| Path params with type coercion | ✅ | ✅ | Direct match |
| Query params, incl. `Query(default=...)` | ✅ | ✅ | Direct match |
| `Depends()` incl. nested/yield deps | ✅ | ✅ | Direct match |
| Pydantic v2 models | ✅ | ✅ (optional extra) | Native `Model`/`field()` if you drop the dependency |
| `APIRouter` + `include_router()` | ✅ | ✅ | Same prefix/tag semantics |
| Background tasks | ✅ | ✅ | `BackgroundTask` |
| OAuth2 / HTTPBearer / API Key | ✅ | ✅ | `api_key_auth()`, `bearer_auth()`, `jwt_auth()` |
| CORS / GZip middleware | ✅ | ✅ | Direct match |
| WebSockets | ✅ | ✅ | `@app.websocket(...)` — production-ready, not "in progress" |
| Multipart/form/file upload | ✅ | ✅ | Includes spooling + per-field limits FastAPI doesn't have by default |
| Session + CSRF | Manual/3rd-party | ✅ built-in | `SessionMiddleware`, `CSRFMiddleware` |
| Sub-app mounting + host routing | ✅ | ✅ | `app.mount()`, `app.mount_host()` |
| OpenAPI + Swagger UI + ReDoc | ✅ | ✅ | Same `/docs`, `/redoc`, `/openapi.json` |
| Background job queue | 3rd-party (Celery, etc.) | ✅ built-in | `InMemoryJobQueue` + Celery/RQ/Redis adapters |
| `TestClient` (`json=`, path query strings) | ✅ | ✅ | Both accepted directly, matching FastAPI's `TestClient`/httpx usage |
| GraphQL | 3rd-party | ❌ not planned | Stay narrow — use a dedicated GraphQL layer if needed |
| Native compiled routing/validation | ❌ | ❌ | Neither compiles routes — see turboapi if you need that tradeoff |

## Things that need small adjustments

**Header binding is explicit, not implicit.** Unlike some FastAPI-adjacent
frameworks that silently bind plain `str` parameters to headers, py-cheema-api
follows FastAPI's own strict semantics — headers always need an explicit
`Header()` marker, with the same `default=`/`required=` behavior you'd expect:

```python
from cheema import Header

@app.get("/headers")
def read_headers(authorization: str = Header(default="missing")):
    return {"authorization": authorization}
```

**Validation error shape.** If you use the native `Model`/`field()` path
instead of Pydantic, error responses follow py-cheema-api's own schema, not
Pydantic's `ValidationError` format. If your client code parses 422 error
bodies, check `docs/api-reference.md` for the exact shape before dropping the
Pydantic extra.

**Settings/env config.** FastAPI apps often hand-roll config loading.
py-cheema-api ships `Cheema.from_env()` and a `CheemaSettings` model — worth
adopting during migration rather than porting a custom config loader.

## Things that don't map over

- Any FastAPI middleware or dependency that reaches into Starlette internals
  directly (rare, but check third-party packages that do this)
- Pydantic v1-only projects — py-cheema-api's optional Pydantic support
  targets v2

## Suggested migration order

1. Swap imports with the Pydantic extra installed — zero behavior change
2. Run your existing test suite against `TestClient`/`AsyncTestClient` — both
   are drop-in compatible with FastAPI's `TestClient` usage patterns
3. Once green, migrate models off Pydantic to `Model`/`field()` file-by-file
   if you want the fully dependency-free path
4. Drop the `[pydantic]` extra once no imports reference it

## Getting help

Open an issue at the repository if you hit a compatibility gap not listed
here — migration parity issues get priority over new feature work.
