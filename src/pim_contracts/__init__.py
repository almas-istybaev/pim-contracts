"""
pim-contracts: Canonical event contracts and AMQP topology for PIM ecosystem.
"""
from pim_contracts.constants import (
    PIM_EVENTS_EXCHANGE,
    PIM_RAW_FEEDS_QUEUE,
    ROUTING_KEY_FEED_ALL,
    ROUTING_KEY_FEED_CANONICAL,
    ROUTING_KEY_FEED_STOCK_UPDATE,
    ROUTING_KEY_FEED_PRICE_UPDATE,
    SCHEMA_VERSION,
)
from pim_contracts.enums import Currency, EventType, SourceType
from pim_contracts.events import (
    BaseEvent,
    CanonicalProductFeedEvent,
    ProductPriceUpdateEvent,
    ProductStockUpdateEvent,
)

__version__ = SCHEMA_VERSION

__all__ = [
    "PIM_EVENTS_EXCHANGE",
    "PIM_RAW_FEEDS_QUEUE",
    "ROUTING_KEY_FEED_ALL",
    "ROUTING_KEY_FEED_CANONICAL",
    "ROUTING_KEY_FEED_STOCK_UPDATE",
    "ROUTING_KEY_FEED_PRICE_UPDATE",
    "SCHEMA_VERSION",
    "SourceType",
    "Currency",
    "EventType",
    "BaseEvent",
    "CanonicalProductFeedEvent",
    "ProductStockUpdateEvent",
    "ProductPriceUpdateEvent",
]
