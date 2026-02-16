"""Monkey-patch for the `requests` library."""

import time
from urllib.parse import urlparse

from smello.config import SmelloConfig


def patch_requests(config: SmelloConfig) -> None:
    """Patch requests.Session.send to capture outgoing HTTP traffic."""
    try:
        import requests
    except ImportError:
        return  # requests not installed, skip

    original_send = requests.Session.send

    def patched_send(self, prepared_request, **kwargs):
        host = urlparse(prepared_request.url).hostname or ""

        if not config.should_capture(host):
            return original_send(self, prepared_request, **kwargs)

        start = time.monotonic()
        response = original_send(self, prepared_request, **kwargs)
        duration = time.monotonic() - start

        try:
            from smello.capture import serialize_request_response
            from smello.transport import send

            payload = serialize_request_response(
                config=config,
                method=prepared_request.method or "GET",
                url=prepared_request.url,
                request_headers=dict(prepared_request.headers),
                request_body=prepared_request.body,
                status_code=response.status_code,
                response_headers=dict(response.headers),
                response_body=response.text,
                duration_s=duration,
                library="requests",
            )
            send(payload)
        except Exception:
            pass  # never break user's code

        return response

    requests.Session.send = patched_send  # type: ignore[assignment]
