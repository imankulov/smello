"""API routes: ingestion endpoint and JSON API."""

import uuid
from urllib.parse import urlparse

from fastapi import APIRouter, Query
from pydantic import BaseModel

from smello_server.models import CapturedRequest

router = APIRouter(prefix="/api")


class RequestData(BaseModel):
    method: str
    url: str
    headers: dict
    body: str | None = None
    body_size: int = 0


class ResponseData(BaseModel):
    status_code: int
    headers: dict
    body: str | None = None
    body_size: int = 0


class MetaData(BaseModel):
    library: str = "unknown"
    python_version: str = ""
    smello_version: str = ""


class CapturePayload(BaseModel):
    id: str | None = None
    timestamp: str | None = None
    duration_ms: int = 0
    request: RequestData
    response: ResponseData
    meta: MetaData = MetaData()


@router.post("/capture", status_code=201)
async def capture(payload: CapturePayload):
    host = urlparse(payload.request.url).hostname or "unknown"

    await CapturedRequest.create(
        id=payload.id or uuid.uuid4(),
        duration_ms=payload.duration_ms,
        method=payload.request.method.upper(),
        url=payload.request.url,
        request_headers=payload.request.headers,
        request_body=payload.request.body,
        request_body_size=payload.request.body_size,
        status_code=payload.response.status_code,
        response_headers=payload.response.headers,
        response_body=payload.response.body,
        response_body_size=payload.response.body_size,
        host=host,
        library=payload.meta.library,
    )
    return {"status": "ok"}


@router.get("/requests")
async def list_requests(
    host: str | None = Query(None),
    method: str | None = Query(None),
    status: int | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(50, le=200),
):
    qs = CapturedRequest.all()
    if host:
        qs = qs.filter(host=host)
    if method:
        qs = qs.filter(method=method.upper())
    if status:
        qs = qs.filter(status_code=status)
    if search:
        qs = qs.filter(url__icontains=search)

    requests = await qs.limit(limit)
    return [
        {
            "id": str(r.id),
            "timestamp": r.timestamp.isoformat(),
            "method": r.method,
            "url": r.url,
            "host": r.host,
            "status_code": r.status_code,
            "duration_ms": r.duration_ms,
        }
        for r in requests
    ]


@router.delete("/requests", status_code=204)
async def clear_requests():
    await CapturedRequest.all().delete()
