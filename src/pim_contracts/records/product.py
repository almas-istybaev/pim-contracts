"""
Master (Golden Record) product and category DTOs exposed by inventory.

Mirrors the export payload of the santeh24 integration:
  - inventory: app/modules/integrations/santeh24/schemas.py
    (Santeh24ProductItem, Santeh24CategoryItem, Santeh24Characteristic)
Consumers: santeh24.kz frontend/src/lib/pim.ts (PIMProduct, PIMCategory).
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TranslationStatus = Literal["machine", "reviewed"]
"""Translation origin: machine-translated or reviewed by a content manager (since 1.12.0)."""

AttributeGroup = Literal["base", "category"]
"""Attribute scope: shared base attribute or category-specific one (since 1.12.0)."""

AttributeSection = Literal["dimensions", "material", "installation", "features"]
"""Storefront section a characteristic is grouped under (since 1.12.0)."""

RelationType = Literal["REQUIRED_COMPONENT", "RECOMMENDED", "COLLECTION_PAIR"]
"""Kind of product-to-product relation (since 1.12.0)."""


class MasterCharacteristicTranslation(BaseModel):
    """Translation of one product characteristic into one storefront language (since 1.7.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    name: str | None = Field(default=None, description="Translated characteristic name")
    value: str | None = Field(
        default=None,
        description=(
            "Translated value in the same format as MasterCharacteristicRecord.value: "
            "options joined with ', ', number with unit, 'Иә'/'Жоқ' for booleans; "
            "None — value is not translated, storefront shows the Russian one"
        ),
    )
    values: list[str] | None = Field(
        default=None,
        description=(
            "Translated options of a multi-select attribute, same order and count as "
            "MasterCharacteristicRecord.values; None for other attribute types (since 1.10.0)"
        ),
    )
    unit: str | None = Field(default=None, description="Translated unit of measurement")
    status: TranslationStatus = Field(
        ...,
        description=(
            "'machine' — draft translated by Claude, 'reviewed' — checked by a human; "
            "'reviewed' only when the name, the unit and every value option are reviewed"
        ),
    )
    is_outdated: bool = Field(
        default=False,
        description="True when the Russian source of any part (name, unit, value option) changed after translation",
    )


class MasterCharacteristicRecord(BaseModel):
    """Key-value characteristic of a master product."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Characteristic name")
    value: str = Field(..., description="Characteristic value")
    values: list[str] | None = Field(
        default=None,
        description=(
            "Separate options of a multi-select attribute; filled only for multi-select, "
            "value stays the options joined with ', ' (since 1.10.0)"
        ),
    )
    code: str | None = Field(
        default=None,
        description="Stable attribute code from the PIM dictionary, e.g. 'width', 'color' (since 1.4.0)",
    )
    group: AttributeGroup | None = Field(
        default=None,
        description="Storefront display group: 'base' (common attributes) or 'category' (category-specific) (since 1.4.0)",
    )
    unit: str | None = Field(
        default=None,
        description="Unit of measurement of the value, e.g. 'cm' (since 1.4.0)",
    )
    numeric_value: float | None = Field(
        default=None,
        description="Numeric form of the value for numeric attributes (since 1.4.0)",
    )
    translations: dict[str, MasterCharacteristicTranslation] = Field(
        default_factory=dict,
        description="Characteristic translations keyed by language code, currently only 'kk' (since 1.7.0)",
    )
    section: AttributeSection | None = Field(
        default=None,
        description=(
            "Storefront product page section: 'dimensions', 'material' (material and color), "
            "'installation' (installation and connection) or 'features' (since 1.9.0)"
        ),
    )
    highlight: int | None = Field(
        default=None,
        ge=1,
        le=4,
        description="Position (1-4) in the key facts shown under the price; None means not a key fact (since 1.9.0)",
    )


class MasterProductTranslation(BaseModel):
    """Translation of product texts into one storefront language (since 1.6.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    name: str | None = Field(default=None, description="Translated product name")
    description: str | None = Field(default=None, description="Translated product description")
    seo_title: str | None = Field(default=None, description="Translated SEO meta title")
    seo_description: str | None = Field(
        default=None,
        description="Translated SEO meta description",
    )
    status: TranslationStatus = Field(
        ...,
        description="'machine' — draft translated by Claude, 'reviewed' — checked by a human",
    )
    is_outdated: bool = Field(
        default=False,
        description="True when the Russian source text changed after this translation was made",
    )


class MasterProductRelation(BaseModel):
    """Link from a master product to another product, set by the content manager in PIM (since 1.8.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    product_id: int = Field(..., description="Id of the linked product (MasterProductRecord.id)")
    relation_type: RelationType = Field(
        ...,
        description=(
            "'REQUIRED_COMPONENT' — needed to install or use the product (e.g. a siphon for a sink), "
            "'RECOMMENDED' — goes well with it, 'COLLECTION_PAIR' — item of the same collection"
        ),
    )


class MasterProductRecord(BaseModel):
    """Master product record as exported by inventory for storefronts."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: int = Field(..., description="Internal product primary key")
    name: str = Field(..., description="Resolved product name (PIM name, else base name)")
    slug: str | None = Field(
        default=None,
        description="Product URL slug built by PIM from pim_name when the admin saves the card (since 1.5.0)",
    )
    previous_slugs: list[str] = Field(
        default_factory=list,
        description="Former slugs of this product; storefront answers them with 301 to the current slug (since 1.5.0)",
    )
    mpn: str | None = Field(default=None, description="Manufacturer part number")
    gpc_id: int | None = Field(default=None, description="Google product category ID")
    brand: str | None = Field(default=None, description="Brand name")
    shipping_weight: str | None = Field(default=None, description="Shipping weight")
    shipping_length: str | None = Field(default=None, description="Shipping length")
    shipping_width: str | None = Field(default=None, description="Shipping width")
    shipping_height: str | None = Field(default=None, description="Shipping height")
    shipping_dimension_unit: str | None = Field(
        default=None,
        description="Unit of shipping_length/width/height, e.g. 'cm' (since 1.4.0)",
    )
    shipping_weight_unit: str | None = Field(
        default=None,
        description="Unit of shipping_weight, e.g. 'kg' (since 1.4.0)",
    )
    category: str | None = Field(default=None, description="Category name")
    category_slug: str | None = Field(
        default=None,
        description="Stable URL slug of the product category (owned by PIM, since 1.3.0)",
    )
    description: str | None = Field(default=None, description="Resolved product description")
    seo_title: str | None = Field(
        default=None,
        description="SEO meta title generated by PIM (since 1.4.0)",
    )
    seo_description: str | None = Field(
        default=None,
        description="SEO meta description generated by PIM (since 1.4.0)",
    )
    characteristics: list[MasterCharacteristicRecord] = Field(
        default_factory=list,
        description="Key-value characteristics",
    )
    price: float = Field(..., description="Retail price")
    price_updated_at: datetime | None = Field(
        default=None,
        description=(
            "UTC time since which the current retail price is in effect; set by PIM whenever the price "
            "changes, null when unknown (since 1.11.0)"
        ),
    )
    cost_price: float | None = Field(
        default=None,
        description="Cost price. Not published by PLP; kept for v1.x compatibility",
    )
    stock: str = Field(..., description="Stock status label, e.g. 'в наличии' or 'нету'")
    stock_quantity: float = Field(
        default=0.0,
        description="Real available quantity (quantity - reserve - quarantine, min 0)",
    )
    photos: list[str] = Field(default_factory=list, description="Absolute public photo URLs")
    translations: dict[str, MasterProductTranslation] = Field(
        default_factory=dict,
        description="Product text translations keyed by language code, currently only 'kk' (since 1.6.0)",
    )
    related: list[MasterProductRelation] = Field(
        default_factory=list,
        description=(
            "Linked products in the order the manager set them; the linked product may be absent "
            "from the export (out of stock, not public) (since 1.8.0)"
        ),
    )


class MasterCategoryTranslation(BaseModel):
    """Translation of category texts into one storefront language (since 1.7.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    name: str | None = Field(default=None, description="Translated category name")
    description: str | None = Field(default=None, description="Translated category description")
    status: TranslationStatus = Field(
        ...,
        description="'machine' — draft translated by Claude, 'reviewed' — checked by a human",
    )
    is_outdated: bool = Field(
        default=False,
        description="True when the Russian source text changed after this translation was made",
    )


class MasterCategoryRecord(BaseModel):
    """Category (taxonomy node) as exported by inventory for storefronts."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: int = Field(..., description="Category primary key")
    name: str = Field(..., description="Category name")
    slug: str | None = Field(
        default=None,
        description=(
            "URL slug owned by PIM (since 1.3.0); it is not changed when the category is renamed, "
            "the admin may change it manually, former values are kept in previous_slugs (since 1.13.0)"
        ),
    )
    previous_slugs: list[str] = Field(
        default_factory=list,
        description="Former slugs of this category; storefront answers them with 301 to the current slug (since 1.13.0)",
    )
    parent_id: int | None = Field(default=None, description="Parent category ID")
    description: str | None = Field(default=None, description="Category description")
    photo: str | None = Field(default=None, description="Public photo URL")
    translations: dict[str, MasterCategoryTranslation] = Field(
        default_factory=dict,
        description="Category text translations keyed by language code, currently only 'kk' (since 1.7.0)",
    )
