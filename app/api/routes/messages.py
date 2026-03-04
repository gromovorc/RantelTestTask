from aiohttp import web
from app.api.handlers.messages import create_message_handler, get_message_handler, get_messages_list_handler, \
    delete_message_handler, update_message_handler

messages_routes = web.RouteTableDef()

messages_routes.post("/tickets/{ticket_id}/messages")(create_message_handler)
messages_routes.get("/tickets/{ticket_id}/messages")(get_messages_list_handler)
messages_routes.get("/messages/{message_id}")(get_message_handler)
messages_routes.patch("/messages/{message_id}")(update_message_handler)
messages_routes.delete("/messages/{message_id}")(delete_message_handler)