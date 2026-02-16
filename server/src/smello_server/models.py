"""Tortoise ORM models for captured HTTP requests."""

from tortoise import fields
from tortoise.models import Model


class CapturedRequest(Model):
    id = fields.UUIDField(pk=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    duration_ms = fields.IntField()

    # Request
    method = fields.CharField(max_length=10)
    url = fields.TextField()
    request_headers: dict = fields.JSONField()
    request_body = fields.TextField(null=True)
    request_body_size = fields.IntField(default=0)

    # Response
    status_code = fields.IntField()
    response_headers: dict = fields.JSONField()
    response_body = fields.TextField(null=True)
    response_body_size = fields.IntField(default=0)

    # Meta
    host = fields.CharField(max_length=255, index=True)
    library = fields.CharField(max_length=50)

    class Meta:
        table = "captured_requests"
        ordering = ["-timestamp"]
