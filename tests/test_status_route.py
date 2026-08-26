from cheema import Cheema, CORSMiddleware, TestClient


def test_status_route_reports_routes_and_middleware():
    app = Cheema(title="My App", version="2.0.0")
    app.use_asgi(CORSMiddleware(allow_origins=["*"]))

    @app.get("/items")
    def list_items():
        return []

    app.add_status_route()

    client = TestClient(app)
    r = client.get("/admin/status")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "My App"
    assert body["version"] == "2.0.0"
    assert body["uptime_seconds"] >= 0
    assert body["inflight_requests"] >= 1
    assert "draining" not in body
    assert any(route["path"] == "/items" and route["method"] == "GET" for route in body["routes"])
    assert any(route["path"] == "/admin/status" for route in body["routes"])
    assert "CORSMiddleware" in body["middleware"]["asgi"]


def test_status_route_excluded_from_openapi_by_default():
    app = Cheema()
    app.add_status_route()

    client = TestClient(app)
    spec = client.get("/openapi.json").json()
    assert "/admin/status" not in spec.get("paths", {})


def test_status_route_included_in_openapi_when_requested():
    app = Cheema()
    app.add_status_route(include_in_schema=True)

    client = TestClient(app)
    spec = client.get("/openapi.json").json()
    assert "/admin/status" in spec.get("paths", {})


def test_status_route_custom_path_and_name():
    app = Cheema()
    app.add_status_route(path="/ops/health", name="ops_status")

    client = TestClient(app)
    r = client.get("/ops/health")
    assert r.status_code == 200
    r_missing = client.get("/admin/status")
    assert r_missing.status_code == 404


def test_status_route_auth_gate_rejects_without_credential():
    app = Cheema()

    def require_token(req):
        return req.headers.get("x-admin-token") == "secret"

    app.add_status_route(auth=require_token)

    client = TestClient(app)
    r = client.get("/admin/status")
    assert r.status_code == 401

    r_ok = client.get("/admin/status", headers={"X-Admin-Token": "secret"})
    assert r_ok.status_code == 200


def test_status_route_extra_hook_sync_and_async():
    app_sync = Cheema()
    app_sync.add_status_route(extra=lambda: {"custom": "value"})
    client_sync = TestClient(app_sync)
    r_sync = client_sync.get("/admin/status")
    assert r_sync.json()["extra"] == {"custom": "value"}

    app_async = Cheema()

    async def extra_hook():
        return {"queue_depth": 3}

    app_async.add_status_route(extra=extra_hook)
    client_async = TestClient(app_async)
    r_async = client_async.get("/admin/status")
    assert r_async.json()["extra"] == {"queue_depth": 3}
