from aiohttp import web
from app.api.handlers.tickets import create_ticket_handler, update_ticket_handler, get_ticket_handler, \
    get_tickets_list_handler

tickets_routes = web.RouteTableDef()

tickets_routes.post("/tickets")(create_ticket_handler)
tickets_routes.get("/tickets/{ticket_id}")(get_ticket_handler)
tickets_routes.get("/tickets")(get_tickets_list_handler)
tickets_routes.patch("/tickets/{ticket_id}")(update_ticket_handler)