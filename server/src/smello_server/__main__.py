"""CLI entry point: `smello-server run` or `python -m smello_server`."""

import argparse
import os

import uvicorn

from smello_server.app import create_app


def main():
    parser = argparse.ArgumentParser(
        prog="smello-server", description="Smello HTTP request inspector"
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Start the Smello server")
    run_parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    run_parser.add_argument(
        "--port", type=int, default=5110, help="Port to bind to (default: 5110)"
    )
    run_parser.add_argument(
        "--db-path", default=None, help="Path to SQLite database file"
    )

    args = parser.parse_args()

    if args.command is None:
        args.command = "run"
        args.host = "0.0.0.0"
        args.port = 5110
        args.db_path = None

    if args.command == "run":
        if args.db_path:
            os.environ["SMELLO_DB_PATH"] = args.db_path

        app = create_app()
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="info",
        )


if __name__ == "__main__":
    main()
