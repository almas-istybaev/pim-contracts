"""
Service summary DTOs for the owner console (since 1.23.0).

Every connected service answers ``GET /internal/summary`` with a ``ServiceSummary``: counters that
need the owner's attention and a few health lines. The service owns its domain, so it chooses the
labels, thresholds (``level``) and links; the console (my.santeh24.kz) only renders them.
No personal data or message texts — counters and timestamps only.
Producers: inventory, price-list-processor, santeh24-instagram. Consumer: console.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SummaryLevel = Literal["ok", "info", "warn", "danger"]


class SummaryItem(BaseModel):
    """One counter on the service tile (since 1.23.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    key: str = Field(..., min_length=1, description="Stable id of the counter within the service, e.g. 'drafts'")
    label: str = Field(..., min_length=1, description="Human-readable label in Russian, chosen by the service")
    value: int | float | str = Field(..., description="The number to show; a string only for pre-formatted values")
    level: SummaryLevel = Field(
        default="info",
        description="Severity decided by the service: ok — nothing to do; info — neutral; warn / danger — needs attention",
    )
    url: str | None = Field(default=None, description="Absolute link to the admin page where the owner handles it")


class SummaryStatus(BaseModel):
    """One line of the 'system state' block (since 1.23.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    key: str = Field(..., min_length=1, description="Stable id of the line within the service, e.g. 'feed'")
    label: str = Field(..., min_length=1, description="Human-readable label in Russian, chosen by the service")
    level: SummaryLevel = Field(default="ok", description="Severity decided by the service")
    at: datetime | None = Field(default=None, description="When it last happened (timezone-aware), if the line is about a moment")
    value: str | None = Field(default=None, description="Short text state, e.g. 'пусто' or '40 дней', if the line is not about a moment")


class ServiceSummary(BaseModel):
    """Answer of ``GET /internal/summary`` (since 1.23.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    service: str = Field(..., min_length=1, description="Service id: 'inventory', 'price-list-processor', 'instagram', ...")
    version: str = Field(..., description="Running version of the service")
    generated_at: datetime = Field(..., description="When the summary was computed (timezone-aware)")
    items: list[SummaryItem] = Field(default_factory=list, description="Counters, most important first")
    status: list[SummaryStatus] = Field(default_factory=list, description="Health lines")
