"""Tests for smello.transport."""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from smello.transport import _json_default, flush, send, shutdown, start_worker


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


def test_flush_waits_for_pending_payloads(capture_server):
    url, captured = capture_server
    start_worker(url)

    for i in range(5):
        send({"id": f"flush-{i}", "request": {}, "response": {}})

    result = flush(timeout=5.0)

    assert result is True
    assert len(captured) == 5


def test_flush_returns_true_when_queue_already_empty(capture_server):
    url, _captured = capture_server
    start_worker(url)

    result = flush(timeout=1.0)
    assert result is True


def test_shutdown_flushes(capture_server):
    url, captured = capture_server
    start_worker(url)

    send({"id": "shutdown-1", "request": {}, "response": {}})

    result = shutdown(timeout=5.0)

    assert result is True
    assert len(captured) == 1


# ---------------------------------------------------------------------------
# _json_default() — fallback serializer
# ---------------------------------------------------------------------------


def test_json_default_handles_bytes():
    assert _json_default(b"\x00\x01\x02") == "b'\\x00\\x01\\x02'"


def test_json_default_handles_arbitrary_objects():
    class Custom:
        def __repr__(self):
            return "Custom()"

    assert _json_default(Custom()) == "Custom()"


def test_json_default_survives_broken_repr():
    class Broken:
        def __repr__(self):
            raise RuntimeError("boom")

    assert _json_default(Broken()) == "<unserializable>"


def test_json_dumps_with_default_serializes_bytes():
    """bytes in a payload dict should serialize via the fallback."""
    payload = {"headers": {"x-bin": b"\n\x02"}, "body": "ok"}
    result = json.loads(json.dumps(payload, default=_json_default))
    assert isinstance(result["headers"]["x-bin"], str)


def test_send_delivers_payload_with_bytes(capture_server):
    """Payloads containing bytes should not crash the transport."""
    url, captured = capture_server
    start_worker(url)

    send({"id": "bytes-test", "headers": {"bin": b"\xff"}, "response": {}})

    deadline = time.monotonic() + 5
    while not captured and time.monotonic() < deadline:
        time.sleep(0.05)

    assert len(captured) == 1
    assert captured[0]["id"] == "bytes-test"
