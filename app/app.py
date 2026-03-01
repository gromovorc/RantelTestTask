from aiohttp import web

from app.api.handlers.clients import create_client_handler
from app.api.handlers.operators import create_operator_handler, update_operator_handler
from app.db.database import engine
from app.db.middlewares import session_middleware

async def db_cleanup_ctx(app: web.Application):
    yield
    await engine.dispose()

async def health(request: web.Request) -> web.Response:
    _ = request["db"]

    return web.json_response({"status": "ok"})

def create_app() -> web.Application:
    app = web.Application(middlewares=[session_middleware])
    app.cleanup_ctx.append(db_cleanup_ctx)

    app.router.add_get("/health", health)
    app.router.add_post("/clients", create_client_handler)

    app.router.add_patch("/operators/{operator_id}", update_operator_handler)
    app.router.add_post("/operators", create_operator_handler)


    return app