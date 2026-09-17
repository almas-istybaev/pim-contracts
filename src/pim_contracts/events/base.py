import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from pim_contracts.constants import SCHEMA_VERSION


class BaseEvent(BaseModel):
    """
    Standard message envelope for all events published to PIM RabbitMQ.
    Guarantees idempotency (event_id), schema versioning, and event timestamps.
    """
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    event_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique message ID for consumer deduplication and idempotency",
    )
    schema_version: str = Field(
        default=SCHEMA_VERSION,
        description="Semantic version of contract schema",
    )
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the event was originally generated",
    )
    trace_id: Optional[str] = Field(
        default=None,
        description="Distributed tracing correlation ID",
    )
