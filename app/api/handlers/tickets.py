from aiohttp import web
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import redis

from app.services.tickets import TicketsService
from app.services.clients import ClientsService
from app.services.operators import OperatorsService

ALLOWED_PRIORITY = {'low', 'normal', 'high'}
ALLOWED_STATUS = {'new', 'in_progress', 'waiting', 'resolved', 'closed'}
ALLOWED_STATUS_TRANSITIONS = {
    "new": {"new", "waiting", "in_progress", "closed"},
    "in_progress": {"resolved", "waiting", "in_progress", "closed"},
    "waiting": {"resolved", "waiting", "in_progress", "closed"},
    "resolved": {"resolved", "closed", "in_progress"},
    "closed": {"closed"}
}

r = redis.Redis(decode_responses=True)

async def check_payload(
        session: AsyncSession,
        client_id: int | None,
        priority: str | None,
        operator_id: int | None,
        status: str | None = None,
        ticket_id: int | None = None,
        subject: str | None = None
):
    if priority is not None and priority not in ALLOWED_PRIORITY:
        raise web.HTTPBadRequest(text="priority is not allowed")

    if client_id is not None:
        client_service = ClientsService(session)

        client = await client_service.get_client(client_id)

        if client is None:
            raise web.HTTPNotFound(text="client not found")

    if operator_id is not None:
        operator_service = OperatorsService(session)

        operator = await operator_service.get_operator(operator_id)

        if operator is None:
            raise web.HTTPNotFound(text="operator not found")

    if ticket_id is not None:
        if status is not None and status not in ALLOWED_STATUS:
            raise web.HTTPBadRequest(text="status is not allowed")

        ticket_service = TicketsService(session)

        ticket = await ticket_service.get_ticket(ticket_id)

        if ticket is None:
            raise web.HTTPNotFound(text="ticket not found")

        if status is not None:
            current_status = await ticket_service.get_ticket_status(ticket_id)

            if status not in ALLOWED_STATUS_TRANSITIONS[current_status]:
                raise web.HTTPBadRequest(text="this status transition is not allowed")

        if all(parameter is None for parameter in (client_id, priority, operator_id, status, subject)):
            raise web.HTTPBadRequest(text="nothing to update")

async def create_ticket_handler(request: web.Request):
    session = request["db"]

    try:
        data = await request.json()
    except Exception as e:
        print(e)
        raise web.HTTPBadRequest(text="invalid json")

    client_id = data.get("client_id")
    priority = data.get("priority")
    subject = data.get("subject")
    operator_id = data.get("operator_id")

    if operator_id is not None:
        try:
            operator_id = int(operator_id)
        except (ValueError, TypeError):
            raise web.HTTPBadRequest(text="operator_id must be int")

    try:
        client_id = int(client_id)
    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="client_id must be int")

    if any(value is None for value in (priority, subject)):
        raise web.HTTPBadRequest(text="priority/subject is empty")

    await check_payload(
        client_id=client_id,
        operator_id=operator_id,
        session=session,
        priority=priority,
    )

    service = TicketsService(session)

    try:
        ticket = await service.add_ticket(
            client_id=client_id,
            priority=priority,
            subject=subject,
            operator_id=operator_id
        )

        await r.delete("dashboard:ticket_counts")

        return web.json_response(ticket, status=201)

    except IntegrityError:
        raise web.HTTPConflict(text="invalid ticket data")

async def update_ticket_handler(request: web.Request):
    session = request["db"]

    try:
        data = await request.json()
    except Exception as e:
        print(e)
        raise web.HTTPBadRequest(text="invalid json")

    ticket_id = request.match_info["ticket_id"]
    client_id = data.get("client_id")
    priority = data.get("priority")
    subject = data.get("subject")
    operator_id = data.get("operator_id")
    status = data.get("status")

    try:
        ticket_id = int(ticket_id)
    except (ValueError, TypeError):
        raise web.HTTPBadRequest(text="ticket_id must be int")

    if operator_id is not None:
        try:
            operator_id = int(operator_id)
        except (ValueError, TypeError):
            raise web.HTTPBadRequest(text="operator_id must be int")

    if client_id is not None:
        try:
            client_id = int(client_id)
        except (ValueError, TypeError):
            raise web.HTTPBadRequest(text="client_id must be int")

    await check_payload(
        client_id=client_id,
        operator_id=operator_id,
        session=session,
        priority=priority,
        ticket_id=ticket_id,
        status=status
    )

    service = TicketsService(session)

    try:
        ticket = await service.update_ticket(
            client_id=client_id,
            operator_id=operator_id,
            priority=priority,
            subject=subject,
            ticket_id=ticket_id,
            status=status
        )

        if status is not None:
            current_status = await service.get_ticket_status(ticket_id)
            if status != current_status:
                await r.delete("dashboard:ticket_counts")

        return web.json_response(ticket, status=200)

    except IntegrityError:
        raise web.HTTPConflict(text="please, check data!")