from aiohttp import web

from app.services.dashboard import DashboardService

async def dashboard_ticket_counts_handler(request: web.Request):

    session = request["db"]
    redis = request.app["redis"]

    service = DashboardService(session, redis)

    counts = await service.get_ticket_counts()

    return web.json_response(counts)