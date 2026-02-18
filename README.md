# Smello

A developer tool that captures outgoing HTTP requests from your Python code and displays them in a local web dashboard.

Think [Mailpit](https://mailpit.axllent.org/) but for HTTP requests. Add two lines to your code, and every outgoing request/response is captured and browsable at `http://localhost:8080`.

## Quick Start

### 1. Start the server

```bash
pip install smello-server
smello-server run
```

Or with Docker:

```bash
docker run -p 8080:8080 ghcr.io/imankulov/smello
```

### 2. Add to your code

```python
import smello
smello.init()

# All outgoing HTTP requests via requests and httpx are now captured
import requests
resp = requests.get("https://api.stripe.com/v1/charges")

import httpx
resp = httpx.get("https://api.openai.com/v1/models")

# Browse captured requests at http://localhost:8080
```

That's it. Two lines, no configuration.

## What Gets Captured

For every outgoing HTTP request, Smello captures:

- Request method, URL, headers, and body
- Response status code, headers, and body
- Timing (duration in milliseconds)
- Which HTTP library was used (requests or httpx)

Sensitive headers (`Authorization`, `X-Api-Key`) are redacted by default.

## Configuration

```python
smello.init(
    server_url="http://localhost:8080",       # where to send captured data
    capture_hosts=["api.stripe.com"],         # only capture requests to these hosts
    capture_all=True,                          # or capture everything (default)
    ignore_hosts=["localhost"],               # never capture these
    redact_headers=["Authorization"],         # replace header values with [REDACTED]
    enabled=True,                              # kill switch
)
```

## API

Smello exposes a JSON API for exploring captured requests from the command line or scripts.

### List captured requests

```bash
# List all captured requests (summary view)
curl -s http://localhost:8080/api/requests | python -m json.tool

# Filter by method
curl -s 'http://localhost:8080/api/requests?method=POST'

# Filter by host
curl -s 'http://localhost:8080/api/requests?host=api.stripe.com'

# Filter by status code
curl -s 'http://localhost:8080/api/requests?status=500'

# Search by URL substring
curl -s 'http://localhost:8080/api/requests?search=checkout'

# Limit results (default: 50, max: 200)
curl -s 'http://localhost:8080/api/requests?limit=10'
```

### Get request details

Returns the full request and response including headers and bodies.

```bash
# Get a specific request by ID
curl -s http://localhost:8080/api/requests/{id} | python -m json.tool
```

### Clear all requests

```bash
curl -X DELETE http://localhost:8080/api/requests
```

## Python Version Support

| Package | Python |
|---------|--------|
| **smello** (client SDK) | >= 3.10 |
| **smello-server** | >= 3.14 |

## Supported Libraries

- **requests** - patches `Session.send()`
- **httpx** - patches `Client.send()` and `AsyncClient.send()`

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
git clone https://github.com/imankulov/smello.git
cd smello

# Install all workspace packages in development mode
uv sync

# Run the server
uv run smello-server run

# Run an example (in another terminal)
uv run python examples/python/basic_requests.py
```

## Architecture

```
Your Python App ──→ Smello Server ──→ Web Dashboard
(smello.init())     (FastAPI+SQLite)   (localhost:8080)
```

- **smello** (client SDK): Monkey-patches `requests` and `httpx` to capture traffic. Sends data to the server via a background thread.
- **smello-server**: FastAPI app with Jinja2 templates and SQLite storage. Receives captured data and serves a browsable dashboard.

## Project Structure

```
smello/
├── server/              # smello-server (FastAPI + Tortoise ORM + SQLite)
│   └── tests/           # Server unit tests
├── clients/python/      # smello client SDK
│   └── tests/           # Client unit tests
├── tests/test_e2e/      # End-to-end tests (workspace-level)
└── examples/python/     # Example scripts
```

## License

MIT
