from aiohttp import web
from sqlalchemy.exc import IntegrityError

from app.services.clients import ClientsService

async def create_client_handler(request: web.Request) -> web.Response:
    session = request["db"]

    try:
        data = await request.json()
    except Exception as e:

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

async def get_client_handler(request: web.Request) -> web.Response:
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

async def get_clients_list_handler(request: web.Request) -> web.Response:
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

async def update_client_handler(request: web.Request) -> web.Response:
    session = request["db"]
    service = ClientsService(session)

    try:
        client_id = int(request.match_info["client_id"])
    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="client_id must be int")

    try:
        data = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="invalid json")

    name = data.get("name")
    email = data.get("email")

    if name is None and email is None:
        raise web.HTTPBadRequest(text="nothing to update")

    if name is not None and not name:
        raise web.HTTPBadRequest(text="name is empty")
    if email is not None and not email:
        raise web.HTTPBadRequest(text="email is empty")

    try:
        client = await service.update_client(client_id=client_id, name=name, email=email)
    except ValueError:
        raise web.HTTPBadRequest(text="nothing to update")
    except IntegrityError:
        raise web.HTTPConflict(text="client with this name and email already exists")

    if client is None:
        raise web.HTTPNotFound(text="client not found")

    return web.json_response(client, status=200)

async def delete_client_handler(request: web.Request) -> web.Response:
    session = request["db"]
    try:
        client_id = int(request.match_info["client_id"])
    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="client_id must be int")

    service = ClientsService(session)
    try:
        deleted = await service.delete_client(client_id)
    except IntegrityError:
        raise web.HTTPConflict(text="client has tickets")

    if not deleted:
        raise web.HTTPNotFound(text="client not found")

    return web.Response(status=204)
