"""
Bundle discount ("скидка за комплект") DTOs exposed by inventory for storefronts (since 1.19.0).

The cart lives only in the browser and is sent to WhatsApp, so the storefront computes the
discount from these published rules plus MasterProductRecord.bundle of each product.
Consumers: santeh24.kz frontend/src/lib/pim.ts.
"""
from pydantic import BaseModel, ConfigDict, Field


class BundleTier(BaseModel):
    """One discount step of the bundle rule (since 1.19.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    roles: int = Field(
        ...,
        ge=1,
        description=(
            "Minimum number of different roles in the cart for this step, e.g. 2, 3, 4 "
            "(4 means '4 or more'); the step with the largest roles not above the cart count applies"
        ),
    )
    percent: int = Field(
        ...,
        ge=0,
        le=100,
        description=(
            "Discount percent applied to the whole cart; on each line it is capped by "
            "MasterProductRecord.bundle.max_percent"
        ),
    )


class BundleRole(BaseModel):
    """Product role counted by the bundle rule, e.g. bath, toilet, furniture (since 1.19.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    key: str = Field(
        ...,
        description=(
            "Stable role key referenced by MasterCategoryRecord.bundle_role and "
            "MasterProductBundle.role; a product whose key is not listed here is an accessory"
        ),
    )
    name: str = Field(..., description="Role name shown to the customer, Russian")
    name_kk: str | None = Field(default=None, description="Role name in Kazakh; null — show the Russian one")
    min_price: int = Field(
        default=0,
        ge=0,
        description=(
            "Minimum unit price in KZT for a product to count for this role; cheaper products "
            "count for no role (accessory) but still get the cart discount"
        ),
    )


class BundleRules(BaseModel):
    """
    Published bundle-discount rule (since 1.19.0).

    Bundle discount does not stack with a promo (MasterProductRecord.promo): a product on promo
    keeps its promo price. Savings are shown in KZT.
    """

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    enabled: bool = Field(
        default=False,
        description="Master switch; false — the storefront shows no bundle discount at all",
    )
    tiers: list[BundleTier] = Field(
        default_factory=list,
        description="Discount steps sorted by roles ascending",
    )
    roles: list[BundleRole] = Field(
        default_factory=list,
        description="Roles counted by the rule, in display order",
    )


class MasterBundleSetTranslation(BaseModel):
    """Translation of bundle set texts into one storefront language (since 1.19.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    name: str | None = Field(default=None, description="Translated set name")
    highlights: list[str] | None = Field(
        default=None,
        description="Translated highlights, same order as the Russian ones (since 1.26.0); null — show the Russian ones",
    )
    description: str | None = Field(
        default=None,
        description="Translated set description (since 1.26.0); null — use the Russian one",
    )


class MasterBundleSetRecord(BaseModel):
    """
    Ready-made set of products assembled by the content manager in the inventory admin (since 1.19.0).

    Published only while every product of the set is in stock; the set price is the bundle
    quote of its products under BundleRules.
    """

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    slug: str = Field(..., description="Stable URL slug of the set, owned by PIM")
    name: str = Field(..., description="Set name, Russian")
    translations: dict[str, MasterBundleSetTranslation] = Field(
        default_factory=dict,
        description="Set text translations keyed by language code, currently only 'kk'",
    )
    image: str | None = Field(default=None, description="Absolute public image URL; null — use product photos")
    highlights: list[str] = Field(
        default_factory=list,
        description=(
            "1-3 short lines, Russian, why the products fit together, in display order, e.g. "
            "'Тумба, раковина и зеркало — по 120 см' (since 1.26.0); empty — show none"
        ),
    )
    description: str | None = Field(
        default=None,
        description=(
            "1-2 sentences, Russian, for the set page and its meta description (since 1.26.0); "
            "null — the storefront keeps the set page out of the index"
        ),
    )
    product_ids: list[int] = Field(
        default_factory=list,
        description="Product ids (MasterProductRecord.id) in display order, one unit each",
    )
