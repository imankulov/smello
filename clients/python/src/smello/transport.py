"""Background transport: sends captured data to the Smello server without blocking."""

import json
import queue
import threading
import urllib.request

_queue: queue.Queue = queue.Queue(maxsize=1000)
_server_url: str = ""


def start_worker(server_url: str) -> None:
    """Start the background worker thread."""
    global _server_url
    _server_url = server_url

    thread = threading.Thread(target=_worker, daemon=True, name="smello-transport")
    thread.start()


def send(payload: dict) -> None:
    """Queue a capture payload for sending. Non-blocking, drops if queue is full."""
    try:
        _queue.put_nowait(payload)
    except queue.Full:
        pass  # drop silently if queue is full


def _worker() -> None:
    """Background worker that sends queued payloads to the server."""
    while True:
        payload = _queue.get()
        try:
            _send_to_server(payload)
        except Exception:
            pass  # silently drop if server is down
        _queue.task_done()


def _send_to_server(payload: dict) -> None:
    """Send a payload to the Smello server using urllib (to avoid recursion)."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{_server_url}/api/capture",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=5)
