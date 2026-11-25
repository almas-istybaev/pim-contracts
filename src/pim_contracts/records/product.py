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
    starts_at: datetime | None = Field(
        default=None,
        description=(
            "UTC time when the promo started: the start date set by the content manager, for "
            "clearance the moment of the markdown. compare_at_price is frozen at this moment. "
            "Used as the start of g:sale_price_effective_date in the Merchant feed; null only for "
            "old records without a start date — consumers must not invent one (since 1.34.0)"
        ),
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


class ProductVideo(BaseModel):
    """Product video review hosted on the PIM CDN (since 1.24.0).

    Exported only after the upload is transcoded to a web-ready MP4 and a poster frame is extracted.
    """

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    url: str = Field(..., description="Absolute public URL of the web-ready MP4 (H.264/AAC)")
    poster: str = Field(..., description="Absolute public URL of the poster frame image")
    duration_sec: int | None = Field(default=None, description="Duration in whole seconds")
    width: int | None = Field(default=None, description="Frame width in pixels")
    height: int | None = Field(default=None, description="Frame height in pixels; height > width for vertical video")
    title: str | None = Field(default=None, description="Video title in Russian")
    title_kk: str | None = Field(default=None, description="Video title in Kazakh")
    uploaded_at: datetime | None = Field(default=None, description="UTC time the video was uploaded to PIM")


class MasterVariantAxis(BaseModel):
    """One axis the members of a variant group differ by, e.g. size or side (since 1.27.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    code: str = Field(
        ...,
        description=(
            "Axis key: 'size', 'side' (left/right), 'mount' (e.g. with frame / without, floor / wall) or 'color'. "
            "Open list: consumers must skip an axis they do not know"
        ),
    )
    label: str = Field(..., description="Axis label in Russian, e.g. 'Размер'")
    label_kk: str | None = Field(default=None, description="Axis label in Kazakh")


class MasterVariantMember(BaseModel):
    """One product of a variant group, the product itself included (since 1.27.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    product_id: int = Field(..., description="MasterProductRecord.id of the member")
    slug: str | None = Field(default=None, description="Storefront slug of the member")
    values: dict[str, str] = Field(
        default_factory=dict,
        description="Axis code -> value in Russian, e.g. {'size': '170×70', 'side': 'Левая'}; a missing axis has no value",
    )
    values_kk: dict[str, str] = Field(
        default_factory=dict,
        description="Axis code -> value in Kazakh; a missing code falls back to `values`",
    )


class MasterVariantGroup(BaseModel):
    """
    Variant group: cards of one model in one category that differ only by the axes, e.g. sizes and left/right
    of one bath (since 1.27.0). Grouped by PIM and confirmed by the content manager; every member keeps its own
    card and canonical URL. Price and stock of the members are not repeated here: take them from the members'
    own records.
    """

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: int = Field(..., description="Variant group id, stable while the group exists")
    axes: list[MasterVariantAxis] = Field(
        default_factory=list, description="Axes in display order (one row of switches per axis)"
    )
    members: list[MasterVariantMember] = Field(
        default_factory=list,
        description=(
            "Active public members, at least two, sorted by axis values; may include a member absent from the "
            "export, which consumers should skip"
        ),
    )


class MasterProductQuestionTranslation(BaseModel):
    """One question with its answer translated into one storefront language (since 1.31.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    question: str = Field(..., description="Translated question")
    answer: str = Field(..., description="Translated answer")
    status: TranslationStatus = Field(
        ...,
        description="'machine' — draft translated by Claude, 'reviewed' — checked by a human",
    )


class MasterProductQuestion(BaseModel):
    """A buyer's question about the product with the store manager's answer (since 1.31.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: int = Field(..., description="Stable PIM id of the question, unique across products")
    question: str = Field(
        ...,
        description="Question in Russian, as edited by the manager; never holds the buyer's name or contacts",
    )
    answer: str = Field(..., description="Manager's answer in Russian, plain text, paragraphs split by a blank line")
    answered_at: datetime = Field(..., description="When the answer was given (UTC)")
    translations: dict[str, MasterProductQuestionTranslation] = Field(
        default_factory=dict,
        description=(
            "Translations keyed by language code, currently only 'kk'; a language is present only while it "
            "translates the current Russian pair, so it is never outdated"
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
    videos: list[ProductVideo] = Field(
        default_factory=list,
        description="Video reviews in display order; empty when the product has none (since 1.24.0)",
    )
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
    sort_rank: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Merchandising rank set by PIM from the product's manual promo and its supplier's rank: lower goes "
            "first. Applies inside the storefront's own stock and photo groups (in-stock with a photo first); "
            "null — no rank, after ranked products (since 1.25.0)"
        ),
    )
    variant_group: MasterVariantGroup | None = Field(
        default=None,
        description="Variant group of the product; null — the product has no confirmed variants (since 1.27.0)",
    )
    brand_slug: str | None = Field(
        default=None,
        description=(
            "Stable URL slug of the product brand, generated by PIM; links the card to the brand x category page "
            "(MasterBrandPageRecord.brand_slug). null — no brand or no slug (since 1.28.0)"
        ),
    )
    size_label: str | None = Field(
        default=None,
        description=(
            "Key size of the product for listing tiles, e.g. '170×70 см': values of the category's size "
            "attributes (set in PIM) joined with '×' plus their common unit, the same text in every language. "
            "null — the category has no size attributes or the product misses one of them (since 1.29.0)"
        ),
    )
    questions: list[MasterProductQuestion] = Field(
        default_factory=list,
        description=(
            "Buyers' questions answered by the store manager and marked for publishing in PIM, newest answer "
            "first. Exported to the own storefront only. Empty — none (since 1.31.0)"
        ),
    )
    content_updated_at: datetime | None = Field(
        default=None,
        description=(
            "UTC time of the last change to the product card that matters to a buyer: name, description, "
            "characteristics (any language), media, retail price, publication or indexing status, a switch "
            "between in stock and out of stock. A stock quantity change that keeps availability does not count. "
            "Storefront sitemap lastmod. Exported to the own storefront only; null when unknown (since 1.33.0)"
        ),
    )
    out_of_stock_since: datetime | None = Field(
        default=None,
        description=(
            "UTC time since which the product has had no stock. The storefront counts days without stock "
            "from it (e.g. noindex after 30 days). null — the product is in stock or the date is unknown; "
            "consumers must not invent one (since 1.35.0)"
        ),
    )


class MasterCategoryFaqItem(BaseModel):
    """One question with its answer on a category page (since 1.30.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    question: str = Field(..., description="Question as a customer asks it")
    answer: str = Field(
        ...,
        description="Answer, plain text; live figures (prices, sizes) are already filled in by PIM on export",
    )


class MasterCategoryTranslation(BaseModel):
    """Translation of category texts into one storefront language (since 1.7.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    name: str | None = Field(default=None, description="Translated category name")
    description: str | None = Field(default=None, description="Translated category description")
    stats_text: str | None = Field(
        default=None,
        description="Translated MasterCategoryRecord.stats_text, generated by PIM (since 1.29.0)",
    )
    faq: list[MasterCategoryFaqItem] = Field(
        default_factory=list,
        description="Translated MasterCategoryRecord.faq, same pairs in the same order; empty — none (since 1.30.0)",
    )
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


class MasterCategoryStats(BaseModel):
    """Live catalog figures of a category with its subcategories, recomputed by PIM on every export (since 1.29.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    product_count: int = Field(..., ge=0, description="Published products, out of stock included")
    in_stock_count: int = Field(..., ge=0, description="Published products in stock")
    price_min: float | None = Field(
        default=None, description="Lowest price the customer pays among in-stock products; null — none in stock"
    )
    price_max: float | None = Field(
        default=None, description="Highest price the customer pays among in-stock products; null — none in stock"
    )


class MasterCategoryKitTranslation(BaseModel):
    """Name of a kit category in one storefront language (since 1.31.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    name: str = Field(..., description="Translated category name")


class MasterCategoryKitItem(BaseModel):
    """A category whose products complete a purchase from another category, «Дополни свой комплект» (since 1.31.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    category_id: int = Field(..., description="MasterCategoryRecord.id of the kit category")
    slug: str = Field(..., description="Slug of the kit category (MasterCategoryRecord.slug), the link target")
    name: str = Field(..., description="Category name in Russian")
    translations: dict[str, MasterCategoryKitTranslation] = Field(
        default_factory=dict,
        description="Category name translations keyed by language code, currently only 'kk'",
    )
    price_min: float = Field(
        ...,
        gt=0,
        description=(
            "Lowest price the customer pays (promo included) among published in-stock products of the kit "
            "category with its subcategories, for «от X ₸»"
        ),
    )
    important: bool = Field(
        default=False,
        description="True — needed to install the product (the storefront marks it «Важно для установки»)",
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
    filter_order: list[str] = Field(
        default_factory=list,
        description=(
            "Attribute codes (MasterCharacteristicRecord.code) of the storefront filters that go first, in this "
            "order, already resolved with inheritance (the nearest category with a non-empty list). The reserved "
            "code 'price' places the price filter. Filters not listed follow in their usual order; unknown codes "
            "are skipped. Empty — no preference (since 1.29.0)"
        ),
    )
    stats: MasterCategoryStats | None = Field(
        default=None,
        description="Live figures of the category with its subcategories; null — not published (since 1.29.0)",
    )
    stats_text: str | None = Field(
        default=None,
        description=(
            "Short Russian paragraph with live figures (models, in stock, price range, brands, common sizes), "
            "generated by PIM from the catalog on every export, without city or store name; null — too few "
            "products in stock. The storefront renders it as is next to the description (since 1.29.0)"
        ),
    )
    faq: list[MasterCategoryFaqItem] = Field(
        default_factory=list,
        description=(
            "Questions and answers about the products of the category, in Russian, set by the content manager in "
            "PIM; live figures are filled in on export and a pair whose figure is unknown is dropped. Product "
            "questions only: delivery, payment and returns differ per storefront and are added by the storefront "
            "itself. Exported to the own storefront only. Empty — none (since 1.30.0)"
        ),
    )
    kit_categories: list[MasterCategoryKitItem] = Field(
        default_factory=list,
        description=(
            "«Дополни свой комплект» for every product of the category: categories to complete the purchase, in "
            "the manager's order, already resolved with inheritance from parent categories. A kit category with "
            "no published product in stock is left out. Exported to the own storefront only. Empty — none "
            "(since 1.31.0)"
        ),
    )
    sort_order: int | None = Field(
        default=None,
        description=(
            "Position of the category among its siblings in the storefront menu and catalog, set by the content "
            "manager: lower goes first. None — after the ordered ones, by id (since 1.32.0)"
        ),
    )
