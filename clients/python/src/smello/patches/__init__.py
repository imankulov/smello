"""Monkey-patches for HTTP client libraries."""

from smello.config import SmelloConfig


def apply_all(config: SmelloConfig) -> None:
    """Apply all available patches."""
    from smello.patches.patch_httpx import patch_httpx
    from smello.patches.patch_requests import patch_requests

    patch_requests(config)
    patch_httpx(config)
