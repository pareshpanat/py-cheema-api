# py-cheema-api

py-cheema-api is a small, fast ASGI web framework built from scratch (stdlib-only) with a focus on predictable performance.

## Features
- Trie router with `{param}` path params
- `APIRouter` composition with prefixes/tags via `include_router()`
- Compiled route plans (signature inspection happens at route registration, not per request)
- Dependency injection with `Depends()` including nested and yield-based dependencies
- Parameter source markers: `Query`, `Header`, `Cookie`, `Form`, `File`
- Built-in validation with `Model` + `field()` (supports `Annotated`, `Literal`, `Enum`, `datetime`, `UUID`, `Decimal`)
- Optional Pydantic v2 compatibility (request/response models + OpenAPI schema integration when installed)
- Multipart/form-data parsing with `UploadFile`
- Multipart hardening: per-file/part/field limits + upload spooling to disk
- `StreamingResponse`, `FileResponse`, `BackgroundTask`, and static file mounting
- Response primitives: `RedirectResponse`, `NegotiatedResponse`, cache header helpers, and `EventSourceResponse` for SSE
- File hardening: `ETag`/`If-None-Match` + byte range (`206`/`416`) support
- WebSocket route support via `@app.websocket(...)`
- Sub-app mounting via `app.mount("/prefix", sub_app)` and host routing via `app.mount_host("*.example.com", app)`
- WebSocket auth helpers (`websocket_token_auth`, `websocket_jwt_auth`) and OpenAPI WS extension docs (`x-cheema-websockets`)
- Security primitives: `api_key_auth()`, `bearer_auth()`, `jwt_auth()`, OAuth2 password/auth-code/client-credentials helpers with OpenAPI security schemas
- Session + CSRF protection primitives (`SessionMiddleware`, `CSRFMiddleware`, CSRF helpers)
- Testing utilities: sync `TestClient` and async `AsyncTestClient` with WebSocket test sessions
- OpenAPI at `/openapi.json`
- Swagger UI at `/docs` and ReDoc at `/redoc`
- Lifespan startup/shutdown handlers
- Lifespan state resources with cleanup guarantees (`app.add_state_resource(...)`)
- App-state dependency helpers (`app.state_dependency(...)`, `app_state_dependency(...)`, `get_app_state(...)`)
- Custom exception handlers with `@app.exception_handler(...)`
- Reliability defaults: request timeout, max body size, max concurrency
- Runtime settings model (`CheemaSettings`) + `Cheema.from_env()` for env-driven deploy config
- Graceful shutdown request draining (`shutdown_drain_timeout`)
- Background job primitives: `InMemoryJobQueue` with retries, delay/schedule, and idempotency keys
- Queue adapters: `CeleryQueueAdapter`, `RQQueueAdapter`, `RedisQueueAdapter`
- CI release gates: Python matrix tests/lint + package build and `twine check`, with trusted publishing workflow
- Benchmark suite + perf regression gates in CI (`benchmarks/bench_runtime.py`)
- `HTTPException` (alias for `HTTPError`) and a `py_cheema_api` import alias for FastAPI-style migrations
- `default=` on `Query`/`Header`/`Cookie`/`Form`/`File`/`Host`/`Body` for FastAPI-style optional params (e.g. `Query(default=10)`)
- Native `Model`/`field()` validated data supports both `item["field"]` and `item.field` access
- `TestClient`/`AsyncTestClient` accept `json=` and query strings embedded in the path, matching FastAPI's `TestClient`
- Pluggable `MemoryCache` primitive, shareable between `ResponseCacheMiddleware` and your own route handlers
- Built-in ops status endpoint via `app.add_status_route()` (route table, middleware stack, uptime, inflight requests, optional auth gate and custom `extra` payload)
- `response_class=` on route decorators (`@app.get(..., response_class=HTMLResponse)`), matching FastAPI's pattern for wrapping plain return values

## What's New

### v1.1.0
FastAPI migration parity fixes — see `MIGRATION.md` for the full guide:
- `HTTPException` alias for `HTTPError`
- `default=` support on all parameter markers (`Query`, `Header`, `Cookie`, `Form`, `File`, `Host`, `Body`)
- Pydantic `BaseModel` responses now serialize cleanly instead of being wrapped in an envelope
- Native `Model` validated data supports attribute access (`item.name`) alongside existing dict access (`item["name"]`)
- `TestClient`/`AsyncTestClient` accept `json=` and parse query strings embedded directly in the path
- `py_cheema_api` import alias, matching the PyPI distribution name

New primitives:
- `MemoryCache`: a pluggable in-process cache with per-entry TTL, usable directly by app code and shareable with `ResponseCacheMiddleware(cache=...)` so both can read/write the same store
- `app.add_status_route()`: a built-in ops status endpoint reporting the route table, middleware stack, app title/version, uptime, and inflight-request count, with an optional `auth` gate and an `extra` hook for custom stats (e.g. queue depth, connection counts)
- `response_class=` on `route()`/`get()`/`post()`/etc. (both `Cheema` and `APIRouter`): wraps a plain return value in the given `Response` subclass, e.g. `@app.get("/page", response_class=HTMLResponse)` returning a bare string. An explicit `Response` return still takes precedence.

### v1.0.0
Initial stable release under the `py-cheema-api` name (renamed from TurboAPI/`py-turbo-api`).

## Stability
- Compatibility policy: `API_COMPATIBILITY.md`
- Current status: v1.1.0

## Install

### From PyPI
```bash
pip install py-cheema-api
```

### Optional: Pydantic v2 compatibility
```bash
pip install "py-cheema-api[pydantic]"
```

PyPI: https://pypi.org/project/py-cheema-api/

## Run example
```bash
uvicorn app:app --reload
```

Open:
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/openapi.json

## Documentation Tracks
- Docs home (GitHub Pages entry): `docs/index.md`
- Complete API reference: `docs/api-reference.md`
- Tutorial: `docs/tutorial.md`
- Advanced: `docs/advanced.md`
- Deployment: `docs/deployment.md`
- Security recipes: `docs/security-recipes.md`
- Why py-cheema-api + benchmark method: `docs/why-py-cheema-api.md`
- Migrating from FastAPI: `MIGRATION.md`
- Benchmark methodology: `BENCHMARKS.md`

## Benchmarks
```bash
python benchmarks/bench_runtime.py --baseline benchmarks/baseline.json --tolerance 1.20 --gate
```

## License
Apache-2.0 (see LICENSE).
