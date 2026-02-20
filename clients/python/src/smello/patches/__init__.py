"""Monkey-patches for HTTP client libraries."""

from smello.config import SmelloConfig
from smello.patches.patch_grpc import patch_grpc
from smello.patches.patch_httpx import patch_httpx
from smello.patches.patch_requests import patch_requests


def apply_all(config: SmelloConfig) -> None:
    """Apply all available patches."""
    patch_requests(config)
    patch_httpx(config)
    patch_grpc(config)
