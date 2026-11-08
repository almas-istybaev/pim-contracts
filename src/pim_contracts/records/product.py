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
    """Link from a master product to another product, set by the content manager in PIM (since 1.8.0)
    or generated by the PIM compatibility rules (since 1.21.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    product_id: int = Field(..., description="Id of the linked product (MasterProductRecord.id)")
    relation_type: RelationType = Field(
        ...,
        description=(
            "'REQUIRED_COMPONENT' — needed to install or use the product (e.g. a siphon for a sink), "
            "'RECOMMENDED' — goes well with it, 'COLLECTION_PAIR' — item of the same collection"
        ),
    )
    kind: Literal["manual", "rule"] | None = Field(
        default=None,
        description=(
            "Who created the link: 'manual' — the content manager, 'rule' — the PIM compatibility generator "
            "from the category companion matrix; null — manual (producer predates 1.21.0) (since 1.21.0)"
        ),
    )
    score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "PIM relevance 0..1 = link weight x attribute compatibility; manual links get 1.0; "
            "null — not scored (producer predates 1.21.0) (since 1.21.0)"
        ),
    )
    reason: list[str] = Field(
        default_factory=list,
        description=(
            "Codes of why the generator matched the pair: 'same_width', 'same_series', 'same_finish', "
            "'same_color', 'same_brand', 'fits_length', 'price_tier'. Consumers ignore unknown codes (since 1.21.0)"
        ),
    )


class MasterProductPromoTranslation(BaseModel):
    """Translation of promo texts into one storefront language (since 1.17.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    name: str | None = Field(default=None, description="Translated campaign name")
    note: str | None = Field(default=None, description="Translated customer-facing note")


class MasterProductPromo(BaseModel):
    """
    Active storefront promo of a product (since 1.17.0).

    Present only while the promo is active. MasterProductRecord.price is then the promo
    price the customer pays; compare_at_price is the regular retail price shown struck through.
    Retail data: not exposed to partners.
    """

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    type: str = Field(
        ...,
        description=(
            "'sale' — dated promo, single product or part of a named campaign (name/slug set); "
            "'clearance' — markdown of a damaged or last unit, lasts until sold out. "
            "Consumers must treat unknown values as a generic promo"
        ),
    )
    compare_at_price: float = Field(
        ...,
        description="Regular retail price before the promo, always greater than the record price",
    )
    until: datetime | None = Field(
        default=None,
        description=(
            "UTC time when the promo ends; null for open-ended promos (clearance). After it the "
            "storefront must show the regular price until the next sync"
        ),
    )
    name: str | None = Field(default=None, description="Campaign name shown to the customer, e.g. 'Наурыз'; null for a single-product promo")
    slug: str | None = Field(
        default=None,
        description="URL-safe campaign slug for grouping products on the storefront promo page",
    )
    note: str | None = Field(
        default=None,
        description="Short customer-facing note, e.g. clearance reason 'повреждена упаковка'",
    )
    translations: dict[str, MasterProductPromoTranslation] = Field(
        default_factory=dict,
        description="Promo text translations keyed by language code, currently only 'kk'",
    )


class MasterProductBundle(BaseModel):
    """
    Bundle-discount data of a product (since 1.19.0).

    Retail data: not exposed to partners. The storefront computes the bundle discount itself
    from BundleRules, because the cart lives only in the browser.
    """

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    role: str | None = Field(
        default=None,
        description=(
            "Bundle role key (BundleRole.key) of the product, already resolved by PIM with inheritance "
            "from parent categories, so consumers need not walk the category tree. null — the product "
            "has no role (accessory). Consumers must treat a key missing from BundleRules.roles as an "
            "accessory: it counts for no role but still gets the discount of the cart"
        ),
    )
    max_percent: int = Field(
        ...,
        ge=0,
        le=100,
        description=(
            "Maximum bundle discount percent allowed on this product. Computed by inventory from the "
            "product margin and the min_margin of its price rule; 0 for excluded products and products "
            "without a purchase price. The cost price is never published, only this cap"
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
    merged_ids: list[int] = Field(
        default_factory=list,
        description=(
            "IDs of duplicate products merged into this one; storefront answers their id URLs with 301 to this "
            "product. Slugs of merged duplicates are added to previous_slugs (since 1.16.0)"
        ),
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
            "Linked products: manual links first in the order the manager set them, then generated ones by "
            "score descending (since 1.21.0); the linked product may be absent from the export "
            "(out of stock, not public) (since 1.8.0)"
        ),
    )
    promo: MasterProductPromo | None = Field(
        default=None,
        description="Active promo; null when the product is sold at the regular price (since 1.17.0)",
    )
    bundle: MasterProductBundle | None = Field(
        default=None,
        description=(
            "Bundle-discount role and cap; null — the product takes no part in the bundle discount "
            "(e.g. rules are off or the producer predates 1.19.0) (since 1.19.0)"
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


class MasterCategoryCompanion(BaseModel):
    """Category whose products complement products of another category (since 1.21.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    category_id: int = Field(..., description="MasterCategoryRecord.id of the companion category, with its descendants")
    category_slug: str | None = Field(default=None, description="Slug of the companion category")
    relation_type: RelationType = Field(
        ...,
        description="'REQUIRED_COMPONENT' — needed to install the product, 'RECOMMENDED' — complements it",
    )
    priority: int = Field(..., ge=1, description="Slot order, 1 = shown first")


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
    cutout: str | None = Field(
        default=None,
        description=(
            "Public CDN URL of a transparent 3D render of a typical product of the category: no background, "
            "about 1:1, trimmed to the edges, WebP or PNG with alpha; uploaded by the content manager in "
            "the inventory admin, shared by all languages. null — not uploaded, the storefront falls back "
            "to photo (since 1.20.0)"
        ),
    )
    translations: dict[str, MasterCategoryTranslation] = Field(
        default_factory=dict,
        description="Category text translations keyed by language code, currently only 'kk' (since 1.7.0)",
    )
    bundle_role: str | None = Field(
        default=None,
        description=(
            "Bundle role key (BundleRole.key) set on this category itself; null — not set here, the role "
            "may be inherited from a parent category. Resolved roles are published in "
            "MasterProductRecord.bundle.role. Consumers must treat an unknown key as an accessory (since 1.19.0)"
        ),
    )
    companions: list[MasterCategoryCompanion] = Field(
        default_factory=list,
        description=(
            "Companion categories already resolved with inheritance from parent categories, ordered by "
            "priority; attribute filters are applied by PIM and not published (since 1.21.0)"
        ),
    )
    substitute_group: str | None = Field(
        default=None,
        description=(
            "Resolved (inherited) key of the group of categories that replace each other, e.g. 'sink', "
            "'mirror'; null — the category substitutes only itself (since 1.21.0)"
        ),
    )
