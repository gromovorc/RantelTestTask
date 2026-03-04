from aiohttp import web
from sqlalchemy.exc import IntegrityError

from app.services.messages import MessagesService

async def create_message_handler(request: web.Request):
    session = request["db"]

    try:
        data = await request.json()
    except Exception as e:
        print(e)
        raise web.HTTPBadRequest(text="invalid json")

    try:
        ticket_id = int(request.match_info["ticket_id"])
        author_type = data.get("author_type")
        author_id = int(data.get("author_id"))
        text = data.get("text")

    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="ticket_id or author_id must be int")

    if author_type not in {"client", "operator"}:
        raise web.HTTPBadRequest(text="author type must be operator/client")

    if not text:
        raise web.HTTPBadRequest(text="text is empty")

    service = MessagesService(session)

    try:
        message = await service.add_message(author_type,
                          author_id,
                          text,
                          ticket_id)

        return web.json_response(message, status=201)

    except IntegrityError:
        raise web.HTTPConflict(text="invalid message data")

async def get_message_handler(request: web.Request):
    session = request["db"]

    service = MessagesService(session)

    try:
        message_id = int(request.match_info["message_id"])
    except ValueError:
        raise web.HTTPBadRequest(text="message_id must be int")

    message = await service.get_message(message_id)

    if not message:
        raise web.HTTPNotFound(text="message not found")
    return web.json_response(message, status=200)

async def get_messages_list_handler(request: web.Request):
    session = request["db"]

    service = MessagesService(session)

    try:
        ticket_id = int(request.match_info["ticket_id"])
    except ValueError:
        raise web.HTTPBadRequest(text="ticket_id must be int")

    try:
        limit, offset = int(request.query.get("limit", "20")), int(request.query.get("offset", "0"))

        if limit < 1 or offset < 0:
            raise web.HTTPBadRequest(text="limit/offset must be positive number")

    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="limit/offset must be int")

    rows = await service.get_messages_list(limit=min(limit, 100), offset=offset, ticket_id=ticket_id)

    if not rows:
        raise web.HTTPNotFound(text="messages by ticket not found")

    return web.json_response(rows, status=200)

async def update_message_handler(request: web.Request) -> web.Response:
    session = request["db"]
    service = MessagesService(session)

    try:
        message_id = int(request.match_info["message_id"])
    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="message_id must be int")

    try:
        data = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="invalid json")

    text = data.get("text")

    if text is None:
        raise web.HTTPBadRequest(text="nothing to update")
    if not text:
        raise web.HTTPBadRequest(text="text is empty")

    try:
        message = await service.update_message(message_id=message_id, text=text)
    except ValueError:
        raise web.HTTPBadRequest(text="nothing to update")
    except IntegrityError:
        raise web.HTTPBadRequest(text="invalid message data")

    if message is None:
        raise web.HTTPNotFound(text="message not found")

    return web.json_response(message, status=200)

async def delete_message_handler(request: web.Request):
    session = request["db"]
    try:
        message_id = int(request.match_info["message_id"])
    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="ticket_id must be int")

    service = MessagesService(session)
    deleted = await service.delete_message(message_id)

    if not deleted:
        raise web.HTTPNotFound(text="message not found")

    return web.Response(status=204)