"""Serialize captured HTTP request/response pairs for sending to the server."""

import time
import uuid

from smello.config import SmelloConfig


def serialize_request_response(
    config: SmelloConfig,
    method: str,
    url: str,
    request_headers: dict,
    request_body: str | bytes | None,
    status_code: int,
    response_headers: dict,
    response_body: str | bytes | None,
    duration_s: float,
    library: str,
) -> dict:
    """Build the capture payload dict."""
    req_headers = _redact_headers(dict(request_headers), config.redact_headers)
    resp_headers = dict(response_headers)

    req_body_str = _body_to_str(request_body)
    resp_body_str = _body_to_str(response_body)

    return {
        "id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_ms": int(duration_s * 1000),
        "request": {
            "method": method,
            "url": url,
            "headers": req_headers,
            "body": req_body_str,
            "body_size": len(request_body) if request_body else 0,
        },
        "response": {
            "status_code": status_code,
            "headers": resp_headers,
            "body": resp_body_str,
            "body_size": len(response_body) if response_body else 0,
        },
        "meta": {
            "library": library,
            "python_version": _python_version(),
            "smello_version": "0.1.0",
        },
    }


def _redact_headers(headers: dict, redact_keys: list[str]) -> dict:
    return {
        k: ("[REDACTED]" if k.lower() in redact_keys else v) for k, v in headers.items()
    }


def _body_to_str(body: str | bytes | None) -> str | None:
    if body is None:
        return None
    if isinstance(body, bytes):
        try:
            return body.decode("utf-8")
        except UnicodeDecodeError:
            return f"<binary: {len(body)} bytes>"
    return body


def _python_version() -> str:
    import sys

    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
