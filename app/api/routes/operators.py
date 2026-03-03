from aiohttp import web
from app.api.handlers.operators import create_operator_handler, get_operator_handler, update_operator_handler

operators_routes = web.RouteTableDef()

operators_routes.post("/operators")(create_operator_handler)
operators_routes.get("/operators/{operator_id}")(get_operator_handler)
operators_routes.patch("/operators/{operator_id}")(update_operator_handler)