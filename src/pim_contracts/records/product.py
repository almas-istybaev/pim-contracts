"""
Master (Golden Record) product and category DTOs exposed by inventory.

Mirrors the export payload of the santeh24 integration:
  - inventory: app/modules/integrations/santeh24/schemas.py
    (Santeh24ProductItem, Santeh24CategoryItem, Santeh24Characteristic)
Consumers: santeh24.kz frontend/src/lib/pim.ts (PIMProduct, PIMCategory).
"""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MasterCharacteristicRecord(BaseModel):
    """Key-value characteristic of a master product."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Characteristic name")
    value: str = Field(..., description="Characteristic value")


class MasterProductRecord(BaseModel):
    """Master product record as exported by inventory for storefronts."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: int = Field(..., description="Internal product primary key")
    name: str = Field(..., description="Resolved product name (PIM name, else base name)")
    mpn: Optional[str] = Field(default=None, description="Manufacturer part number")
    gpc_id: Optional[int] = Field(default=None, description="Google product category ID")
    brand: Optional[str] = Field(default=None, description="Brand name")
    shipping_weight: Optional[str] = Field(default=None, description="Shipping weight")
    shipping_length: Optional[str] = Field(default=None, description="Shipping length")
    shipping_width: Optional[str] = Field(default=None, description="Shipping width")
    shipping_height: Optional[str] = Field(default=None, description="Shipping height")
    category: Optional[str] = Field(default=None, description="Category name")
    category_slug: Optional[str] = Field(
        default=None,
        description="Stable URL slug of the product category (owned by PIM, since 1.3.0)",
    )
    description: Optional[str] = Field(default=None, description="Resolved product description")
    characteristics: List[MasterCharacteristicRecord] = Field(
        default_factory=list,
        description="Key-value characteristics",
    )
    price: float = Field(..., description="Retail price")
    cost_price: Optional[float] = Field(default=None, description="Cost price")
    stock: str = Field(..., description="Stock status label, e.g. 'в наличии' or 'нету'")
    stock_quantity: float = Field(
        default=0.0,
        description="Real available quantity (quantity - reserve - quarantine, min 0)",
    )
    photos: List[str] = Field(default_factory=list, description="Absolute public photo URLs")


class MasterCategoryRecord(BaseModel):
    """Category (taxonomy node) as exported by inventory for storefronts."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: int = Field(..., description="Category primary key")
    name: str = Field(..., description="Category name")
    slug: Optional[str] = Field(
        default=None,
        description="Stable URL slug owned by PIM; does not change on rename (since 1.3.0)",
    )
    parent_id: Optional[int] = Field(default=None, description="Parent category ID")
    description: Optional[str] = Field(default=None, description="Category description")
    photo: Optional[str] = Field(default=None, description="Public photo URL")
