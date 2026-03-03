from aiohttp import web
from app.api.handlers.clients import create_client_handler, get_client_handler, get_clients_list_handler

clients_routes = web.RouteTableDef()

clients_routes.post("/clients")(create_client_handler)
clients_routes.get("/clients/{client_id}")(get_client_handler)
clients_routes.get("/clients")(get_clients_list_handler)