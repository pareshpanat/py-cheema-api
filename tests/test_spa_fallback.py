import os
import tempfile

from cheema import Cheema, TestClient


def _make_spa_dist(tmp):
    os.makedirs(os.path.join(tmp, "assets"), exist_ok=True)
    with open(os.path.join(tmp, "index.html"), "w") as f:
        f.write("<html><body>SPA shell</body></html>")
    with open(os.path.join(tmp, "assets", "app.js"), "w") as f:
        f.write("console.log('app')")


def test_spa_fallback_disabled_by_default_returns_404():
    with tempfile.TemporaryDirectory() as tmp:
        _make_spa_dist(tmp)
        app = Cheema()
        app.mount_static("/", tmp)

        client = TestClient(app)
        r = client.get("/dashboard/settings")
        assert r.status_code == 404


def test_spa_fallback_serves_index_for_extensionless_routes():
    with tempfile.TemporaryDirectory() as tmp:
        _make_spa_dist(tmp)
        app = Cheema()
        app.mount_static("/", tmp, spa_fallback=True)

        client = TestClient(app)
        r = client.get("/dashboard/settings")
        assert r.status_code == 200
        assert r.text == "<html><body>SPA shell</body></html>"


def test_spa_fallback_serves_index_at_root():
    with tempfile.TemporaryDirectory() as tmp:
        _make_spa_dist(tmp)
        app = Cheema()
        app.mount_static("/", tmp, spa_fallback=True)

        client = TestClient(app)
        r = client.get("/")
        assert r.status_code == 200
        assert r.text == "<html><body>SPA shell</body></html>"


def test_spa_fallback_still_404s_missing_real_assets():
    with tempfile.TemporaryDirectory() as tmp:
        _make_spa_dist(tmp)
        app = Cheema()
        app.mount_static("/", tmp, spa_fallback=True)

        client = TestClient(app)
        r = client.get("/assets/missing.js")
        assert r.status_code == 404


def test_spa_fallback_still_serves_real_files_normally():
    with tempfile.TemporaryDirectory() as tmp:
        _make_spa_dist(tmp)
        app = Cheema()
        app.mount_static("/", tmp, spa_fallback=True)

        client = TestClient(app)
        r = client.get("/assets/app.js")
        assert r.status_code == 200
        assert r.text == "console.log('app')"


def test_spa_fallback_custom_index_file():
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "shell.html"), "w") as f:
            f.write("<html>custom shell</html>")
        app = Cheema()
        app.mount_static("/", tmp, spa_fallback=True, index_file="shell.html")

        client = TestClient(app)
        r = client.get("/some/route")
        assert r.status_code == 200
        assert r.text == "<html>custom shell</html>"


def test_spa_fallback_without_index_file_present_404s():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "assets"), exist_ok=True)
        with open(os.path.join(tmp, "assets", "app.js"), "w") as f:
            f.write("console.log('app')")
        app = Cheema()
        app.mount_static("/", tmp, spa_fallback=True)

        client = TestClient(app)
        r = client.get("/dashboard")
        assert r.status_code == 404
