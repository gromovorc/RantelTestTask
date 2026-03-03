from aiohttp import web
from app.api.handlers.dashboard import dashboard_ticket_counts_handler

dashboard_routes = web.RouteTableDef()

dashboard_routes.get("/dashboard/ticket-counts")(dashboard_ticket_counts_handler)