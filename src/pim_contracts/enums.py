"""
Shared Domain Enums for Supplier Ingestion & PIM.
"""
from enum import Enum


class SourceType(str, Enum):
    """Origin channel of supplier feed."""
    MOYSKLAD_API = "moysklad_api"
    MULTI_SOURCE_SCRAPER = "multi_source_scraper"
    TELEGRAM_EXCEL = "telegram_excel"
    MANUAL_IMPORT = "manual_import"


class Currency(str, Enum):
    """Standard ISO currency codes."""
    KZT = "KZT"
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"


class EventType(str, Enum):
    """Event types published to message broker."""
    CATALOG_FULL = "catalog_full"
    STOCK_UPDATED = "stock_updated"
    PRICE_UPDATED = "price_updated"
