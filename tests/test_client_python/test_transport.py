"""Tests for smello.transport."""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from smello.transport import send, start_worker


class _CaptureHandler(BaseHTTPRequestHandler):
    captured: list = []

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        _CaptureHandler.captured.append(body)
        self.send_response(201)
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')

    def log_message(self, format, *args):
        pass


@pytest.fixture()
def capture_server():
    """Start a minimal HTTP server that records POSTed payloads."""
    _CaptureHandler.captured = []
    server = HTTPServer(("127.0.0.1", 0), _CaptureHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}", _CaptureHandler.captured
    server.shutdown()


def test_send_delivers_payload(capture_server):
    url, captured = capture_server
    start_worker(url)

    payload = {
        "id": "test-transport-1",
        "request": {"method": "GET", "url": "https://example.com"},
        "response": {"status_code": 200},
    }
    send(payload)

    deadline = time.monotonic() + 5
    while not captured and time.monotonic() < deadline:
        time.sleep(0.05)

    assert len(captured) == 1
    assert captured[0]["id"] == "test-transport-1"
