import asyncio
import contextvars
import functools
import inspect
import sys
from contextlib import asynccontextmanager


class _CompatTimeout:
    """Backport of asyncio.timeout()'s cancel-on-expiry behavior for Python < 3.11."""

    __slots__ = ("_seconds", "_task", "_handle", "_cancelling")

    def __init__(self, seconds):
        self._seconds = seconds
        self._task = None
        self._handle = None
        self._cancelling = False

    def _on_timeout(self):
        self._cancelling = True
        self._task.cancel()

    async def __aenter__(self):
        self._task = asyncio.current_task()
        loop = asyncio.get_running_loop()
        self._handle = loop.call_later(self._seconds, self._on_timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._handle.cancel()
        if exc_type is asyncio.CancelledError and self._cancelling:
            raise TimeoutError from None
        return False


@asynccontextmanager
async def timeout(seconds: float):
    if seconds is None or seconds <= 0:
        yield
        return
    if sys.version_info >= (3, 11):
        async with asyncio.timeout(seconds):
            yield
    else:
        async with _CompatTimeout(seconds):
            yield

def is_async_callable(fn):
    return inspect.iscoroutinefunction(fn) or inspect.iscoroutinefunction(getattr(fn, "__call__", None))

async def _to_thread_compat(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, call)

async def run_sync(func, *args, **kwargs):
    if sys.version_info >= (3, 9):
        return await asyncio.to_thread(func, *args, **kwargs)
    return await _to_thread_compat(func, *args, **kwargs)

async def call_callable(fn, *args, **kwargs):
    if is_async_callable(fn):
        return await fn(*args, **kwargs)
    result = await run_sync(fn, *args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result
