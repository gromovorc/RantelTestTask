from aiohttp import web

from app.db.database import async_session_maker

@web.middleware
async def session_middleware(
    request,
    handler
) -> web.StreamResponse:
    session = async_session_maker()
    request["db"] = session

    try:
        response = await handler(request)
        return response
    finally:
        await session.close()

