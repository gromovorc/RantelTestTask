from aiohttp import web

from .clients import clients_routes
from .messages import messages_routes
from .operators import operators_routes
from .tickets import tickets_routes
from .dashboard import dashboard_routes

def setup_routes(app: web.Application) -> None:
    app.add_routes(clients_routes)
    app.add_routes(operators_routes)
    app.add_routes(tickets_routes)
    app.add_routes(dashboard_routes)
    app.add_routes(messages_routes)