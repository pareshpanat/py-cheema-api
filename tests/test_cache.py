import asyncio
import json

from cheema import Cheema, MemoryCache, ResponseCacheMiddleware


async def run_http(app, method="GET", path="/", query="", headers=None, body=b""):
    sent = []
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": query.encode("utf-8"),
        "headers": headers or [],
    }
    events = [{"type": "http.request", "body": body, "more_body": False}]

    async def receive():
        if events:
            return events.pop(0)
        return {"type": "http.disconnect"}

    async def send(msg):
        sent.append(msg)

    await app(scope, receive, send)
    start = next(m for m in sent if m["type"] == "http.response.start")
    body_out = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
    return start, body_out


def test_memory_cache_get_set_default():
    async def scenario():
        cache = MemoryCache()
        assert await cache.get("missing") is None
        assert await cache.get("missing", "fallback") == "fallback"
        await cache.set("a", 1)
        assert await cache.get("a") == 1

    asyncio.run(scenario())


def test_memory_cache_ttl_expiry():
    async def scenario():
        cache = MemoryCache()
        await cache.set("k", "v", ttl=0.01)
        assert await cache.get("k") == "v"
        await asyncio.sleep(0.05)
        assert await cache.get("k") is None

    asyncio.run(scenario())


def test_memory_cache_delete_and_clear():
    async def scenario():
        cache = MemoryCache()
        await cache.set("a", 1)
        await cache.set("b", 2)
        await cache.delete("a")
        assert await cache.get("a") is None
        assert await cache.get("b") == 2
        await cache.clear()
        assert await cache.get("b") is None

    asyncio.run(scenario())


def test_memory_cache_get_or_set_sync_and_async_factory():
    async def scenario():
        cache = MemoryCache()
        calls = []

        def factory():
            calls.append(1)
            return 42

        assert await cache.get_or_set("k", factory) == 42
        assert await cache.get_or_set("k", factory) == 42
        assert len(calls) == 1

        async def afactory():
            return 99

        assert await cache.get_or_set("k2", afactory) == 99

    asyncio.run(scenario())


def test_memory_cache_eviction_prefers_soonest_expiry():
    async def scenario():
        cache = MemoryCache(max_entries=2)
        await cache.set("soon", 1, ttl=1)
        await cache.set("later", 2, ttl=1000)
        await cache.set("newest", 3, ttl=1000)
        assert len(cache._store) == 2
        assert await cache.get("soon") is None
        assert await cache.get("later") == 2
        assert await cache.get("newest") == 3

    asyncio.run(scenario())


def test_response_cache_middleware_default_backend_caches():
    app = Cheema()
    app.use_asgi(ResponseCacheMiddleware(ttl_seconds=30))
    calls = {"n": 0}

    @app.get("/cached")
    async def cached():
        calls["n"] += 1
        return {"value": calls["n"]}

    s1, b1 = asyncio.run(run_http(app, path="/cached"))
    s2, b2 = asyncio.run(run_http(app, path="/cached"))
    assert s1["status"] == 200 and s2["status"] == 200
    assert json.loads(b1.decode("utf-8"))["value"] == 1
    assert json.loads(b2.decode("utf-8"))["value"] == 1
    assert calls["n"] == 1


def test_response_cache_middleware_shared_cache_visible_to_app_code():
    shared = MemoryCache()
    app = Cheema()
    app.use_asgi(ResponseCacheMiddleware(ttl_seconds=30, cache=shared))

    @app.get("/cached")
    async def cached():
        return {"value": 1}

    asyncio.run(run_http(app, path="/cached"))
    assert len(shared._store) == 1

    async def read_shared():
        key = next(iter(shared._store))
        return await shared.get(key)

    status, headers, body = asyncio.run(read_shared())
    assert status == 200
    assert json.loads(body.decode("utf-8")) == {"value": 1}
