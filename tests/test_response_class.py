from cheema import APIRouter, Cheema, HTMLResponse, JSONResponse, TestClient


def test_response_class_wraps_plain_string_return():
    app = Cheema()

    @app.get("/welcome", response_class=HTMLResponse)
    async def welcome_message():
        return "<h1>Hello, World!</h1><p>Raw HTML response</p>"

    client = TestClient(app)
    r = client.get("/welcome")
    assert r.status_code == 200
    assert r.headers.get("content-type") == "text/html; charset=utf-8"
    assert r.text == "<h1>Hello, World!</h1><p>Raw HTML response</p>"


def test_response_class_without_it_returns_plain_text():
    app = Cheema()

    @app.get("/plain")
    def plain():
        return "<h1>Hello</h1>"

    client = TestClient(app)
    r = client.get("/plain")
    assert r.headers.get("content-type") == "text/plain; charset=utf-8"


def test_response_class_combines_with_status_code():
    app = Cheema()

    @app.get("/created", response_class=HTMLResponse, status_code=201)
    def created():
        return "<p>done</p>"

    client = TestClient(app)
    r = client.get("/created")
    assert r.status_code == 201
    assert r.headers.get("content-type") == "text/html; charset=utf-8"


def test_response_class_explicit_response_return_wins():
    app = Cheema()

    @app.get("/override", response_class=HTMLResponse)
    def override():
        return JSONResponse({"explicit": True})

    client = TestClient(app)
    r = client.get("/override")
    assert r.headers.get("content-type") == "application/json; charset=utf-8"
    assert r.json() == {"explicit": True}


def test_response_class_propagates_through_include_router():
    router = APIRouter()

    @router.get("/page", response_class=HTMLResponse)
    def page():
        return "<h2>From a router</h2>"

    app = Cheema()
    app.include_router(router, prefix="/site")

    client = TestClient(app)
    r = client.get("/site/page")
    assert r.headers.get("content-type") == "text/html; charset=utf-8"
    assert r.text == "<h2>From a router</h2>"


def test_response_class_json_response_uses_app_custom_encoders():
    class Money:
        def __init__(self, cents):
            self.cents = cents

    app = Cheema()
    app.json_encoder(Money, lambda m: m.cents / 100)

    @app.get("/price", response_class=JSONResponse)
    def price():
        return {"amount": Money(1999)}

    client = TestClient(app)
    r = client.get("/price")
    assert r.json() == {"amount": 19.99}
