from aiohttp import web
from sqlalchemy.exc import IntegrityError

from app.services.clients import ClientsService

async def create_client_handler(request: web.Request):
    session = request["db"]

    try:
        data = await request.json()
    except Exception as e:
        print(e)
        raise web.HTTPBadRequest(text="invalid json")

    name, email = data.get("name"), data.get("email")

    if not name or not email:
        raise web.HTTPBadRequest(text="name or email is empty!")

    service = ClientsService(session)

    try:
        client = await service.add_client(name=name, email=email)

        return web.json_response(client, status=201)

    except IntegrityError:
        raise web.HTTPConflict(text="client with this email and name already exists")

async def get_client_handler(request: web.Request):
    session = request["db"]

    service = ClientsService(session)

    try:
        client_id = int(request.match_info["client_id"])
    except ValueError:
        raise web.HTTPBadRequest(text="client_id must be int")

    client = await service.get_client(client_id)

    if not client:
        raise web.HTTPNotFound(text="client not found")
    return web.json_response(client, status=200)

async def get_clients_list_handler(request: web.Request):
    session = request["db"]

    service = ClientsService(session)

    try:
        limit, offset = int(request.query.get("limit", "20")), int(request.query.get("offset", "0"))

        if limit < 1 or offset < 0:
            raise web.HTTPBadRequest(text="limit/offset must be positive number")

    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="limit/offset must be int")

    rows = await service.get_clients_list(limit=min(limit, 100), offset=offset)

    if not rows:
        raise web.HTTPNotFound(text="clients not found")
    return web.json_response(rows, status=200)
