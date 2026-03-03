import asyncio
import contextlib

from aiohttp import web

from app.api.routes import setup_routes
from app.background_tasks.close_waiting import close_tickets_in_waiting
from app.db.database import engine
from app.db.middlewares import session_middleware
from app.cache.redis import create_redis

async def db_cleanup_ctx(app: web.Application):
    yield
    await engine.dispose()

async def redis_ctx(app: web.Application):
    app["redis"] = create_redis()
    yield
    await app["redis"].close()

async def close_tickets_in_waiting_ctx(app):
    task = asyncio.create_task(close_tickets_in_waiting(app))
    yield
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task

async def health(request: web.Request) -> web.Response:
    _ = request["db"]

    return web.json_response({"status": "ok"})

def create_app() -> web.Application:
    app = web.Application(middlewares=[session_middleware])

    app.cleanup_ctx.append(db_cleanup_ctx)
    app.cleanup_ctx.append(redis_ctx)
    app.cleanup_ctx.append(close_tickets_in_waiting_ctx)

    app.router.add_get("/health", health)

    setup_routes(app)
    return app