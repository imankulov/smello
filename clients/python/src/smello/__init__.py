"""Smello - Capture outgoing HTTP requests automatically."""

from smello.config import SmelloConfig

__version__ = "0.1.0"

_config: SmelloConfig | None = None


def init(
    server_url: str = "http://localhost:8080",
    capture_hosts: list[str] | None = None,
    capture_all: bool = True,
    ignore_hosts: list[str] | None = None,
    redact_headers: list[str] | None = None,
    enabled: bool = True,
) -> None:
    """Initialize Smello. Patches requests and httpx to capture outgoing HTTP traffic."""
    global _config

    if not enabled:
        return

    _config = SmelloConfig(
        server_url=server_url.rstrip("/"),
        capture_hosts=capture_hosts or [],
        capture_all=capture_all,
        ignore_hosts=ignore_hosts or [],
        redact_headers=[
            h.lower() for h in (redact_headers or ["authorization", "x-api-key"])
        ],
    )

    # Always ignore the smello server itself
    from urllib.parse import urlparse

    server_host = urlparse(_config.server_url).hostname
    if server_host and server_host not in _config.ignore_hosts:
        _config.ignore_hosts.append(server_host)

    # Start transport worker
    from smello.transport import start_worker

    start_worker(_config.server_url)

    # Apply patches
    from smello.patches import apply_all

    apply_all(_config)
