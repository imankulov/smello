"""FastAPI application setup with Tortoise ORM."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from smello_server.routes.api import router as api_router
from smello_server.routes.web import router as web_router

PACKAGE_DIR = Path(__file__).parent
STATIC_DIR = PACKAGE_DIR / "static"


def _get_db_url() -> str:
    db_path = os.environ.get("SMELLO_DB_PATH")
    if db_path:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite://{db_path}"
    default_dir = Path.home() / ".smello"
    default_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite://{default_dir / 'smello.db'}"


def create_app(db_url: str | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(title="Smello")

    application.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    application.include_router(api_router)
    application.include_router(web_router)

    register_tortoise(
        application,
        db_url=db_url or _get_db_url(),
        modules={"models": ["smello_server.models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )

    return application
