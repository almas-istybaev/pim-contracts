from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import Field
from pim_contracts.enums import Currency, SourceType
from pim_contracts.events.base import BaseEvent


class CanonicalProductFeedEvent(BaseEvent):
    """
    Canonical product state payload emitted when an item is created or updated.
    Supports decoupled prices and out-of-stock items (stock = 0).
    """
    supplier_id: str = Field(..., min_length=1, description="Supplier slug / ID")
    supplier_sku: str = Field(..., min_length=1, description="Supplier SKU / article")
    normalized_mpn: Optional[str] = Field(default=None, description="Sanitized alphanumeric MPN")
    name: str = Field(..., min_length=1, description="Product title / name")
    description: Optional[str] = Field(default=None, description="Product description if provided")
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw warehouse properties (physical_stock, reserve, uom, in_transit)",
    )

    raw_price: Decimal = Field(default=Decimal("0.0"), ge=0, description="Latest price parsed from supplier list or API")
    stock: int = Field(default=0, ge=0, description="Available quantity for sale: max(physical_stock - reserve, 0)")
    currency: Currency = Field(default=Currency.KZT, description="Currency ISO code")

    is_wholesale_available: bool = Field(default=True, description="Wholesale channel availability")
    is_retail_available: bool = Field(default=True, description="Retail channel availability")

    raw_media_urls: List[str] = Field(
        default_factory=list,
        description="Raw source media URLs without local downloading or processing",
    )
    source_channel: SourceType = Field(default=SourceType.UNKNOWN, description="Source origin channel")
    payload_hash: Optional[str] = Field(default=None, description="MD5 composite state hash (price_hash:stock_hash)")


class ProductStockUpdateEvent(BaseEvent):
    """
    Lightweight event emitted on inventory delta or sitemap absence zeroing.
    """
    supplier_id: str = Field(..., min_length=1)
    supplier_sku: str = Field(..., min_length=1)
    normalized_mpn: Optional[str] = Field(default=None)
    raw_price: Decimal = Field(default=Decimal("0.0"), ge=0)
    stock: int = Field(default=0, ge=0)
    currency: Currency = Field(default=Currency.KZT)
    payload_hash: Optional[str] = Field(default=None)
    reason: Optional[str] = Field(default=None)


class ProductPriceUpdateEvent(BaseEvent):
    """
    Lightweight event emitted when only price has changed.
    """
    supplier_id: str = Field(..., min_length=1)
    supplier_sku: str = Field(..., min_length=1)
    normalized_mpn: Optional[str] = Field(default=None)
    old_price: Optional[Decimal] = Field(default=None)
    new_price: Decimal = Field(default=Decimal("0.0"), ge=0)
    currency: Currency = Field(default=Currency.KZT)
    payload_hash: Optional[str] = Field(default=None)
