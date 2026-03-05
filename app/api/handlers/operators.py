from aiohttp import web
from sqlalchemy.exc import IntegrityError

from app.services.operators import OperatorsService

ALLOWED_STATUS = {"online", "offline", "busy"}

async def create_operator_handler(request: web.Request) -> web.Response:
    session = request["db"]

    try:
        data = await request.json()
    except Exception as e:
        raise web.HTTPBadRequest(text="invalid json")

    name, email, status = data.get("name"), data.get("email"), data.get("status")

    if not name or not email:
        raise web.HTTPBadRequest(text="name or email is empty!")

    service = OperatorsService(session)

    try:
        operator = await service.add_operator(name=name, email=email, status=status)

        return web.json_response(operator, status=201)

    except IntegrityError:
        raise web.HTTPConflict(text="operator with this email and name already exists")

async def get_operator_handler(request: web.Request) -> web.Response:
    session = request["db"]

    service = OperatorsService(session)

    try:
        operator_id = int(request.match_info["operator_id"])
    except ValueError:
        raise web.HTTPBadRequest(text="operator_id must be int")

    operator = await service.get_operator(operator_id)

    if not operator:
        raise web.HTTPNotFound(text="operator not found")
    return web.json_response(operator, status=200)

async def get_operators_list_handler(request: web.Request) -> web.Response:
    session = request["db"]

    service = OperatorsService(session)

    try:
        limit, offset = int(request.query.get("limit", "20")), int(request.query.get("offset", "0"))

        if limit < 1 or offset < 0:
            raise web.HTTPBadRequest(text="limit/offset must be positive number")

    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="limit/offset must be int")

    rows = await service.get_operators_list(limit=min(limit, 100), offset=offset)

    if not rows:
        raise web.HTTPNotFound(text="operators not found")

    return web.json_response(rows, status=200)

async def update_operator_handler(request: web.Request) -> web.Response:
    session = request["db"]

    try:
        data = await request.json()
    except Exception as e:
        raise web.HTTPBadRequest(text="invalid json")

    try:
        operator_id = int(request.match_info["operator_id"])
        name = data.get("name")
        email = data.get("email")
        status = data.get("status")
    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="operator_id must be int")

    service = OperatorsService(session)

    if status is not None and status not in ALLOWED_STATUS:
        raise web.HTTPBadRequest(text="status is not allowed")

    try:
        operator = await service.update_operator(operator_id=operator_id, name=name, email=email, status=status)

        if not operator:
            raise web.HTTPNotFound(text="operator not found")

        return web.json_response(operator, status=200)

    except IntegrityError:
        raise web.HTTPConflict(text="please, check status, email and name!")
    except ValueError:
        raise web.HTTPBadRequest(text="check parameters")

async def delete_operator_handler(request: web.Request) -> web.Response:
    session = request["db"]
    try:
        operator_id = int(request.match_info["operator_id"])
    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="client_id must be int")

    service = OperatorsService(session)
    try:
        deleted = await service.delete_operator(operator_id)
    except IntegrityError:
        raise web.HTTPConflict(text="operator has tickets")

    if not deleted:
        raise web.HTTPNotFound(text="operator not found")

    return web.Response(status=204)
