from aiohttp import web
from sqlalchemy.exc import IntegrityError

from app.services.operators import OperatorsService

ALLOWED_STATUS = {"online", "offline", "busy"}

async def create_operator_handler(request: web.Request):
    session = request["db"]

    try:
        data = await request.json()
    except Exception as e:
        print(e)
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

async def update_operator_handler(request: web.Request):
    session = request["db"]

    try:
        data = await request.json()
    except Exception as e:
        print(e)
        raise web.HTTPBadRequest(text="invalid json")

    try:
        operator_id, name, email, status = int(request.match_info["operator_id"]), data.get("name"), data.get("email"), data.get("status")
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
