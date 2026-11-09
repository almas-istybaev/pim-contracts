"""
pim-contracts: Canonical event contracts and AMQP topology for PIM ecosystem.
"""
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from pim_contracts.constants import (
    PIM_EVENTS_EXCHANGE,
    PIM_RAW_FEEDS_QUEUE,
    ROUTING_KEY_FEED_ALL,
    ROUTING_KEY_FEED_CANONICAL,
    ROUTING_KEY_FEED_PRICE_UPDATE,
    ROUTING_KEY_FEED_STOCK_UPDATE,
    SCHEMA_VERSION,
)
from pim_contracts.enums import Currency, EventType, SourceType
from pim_contracts.events import (
    BaseEvent,
    CanonicalProductFeedEvent,
    ProductPriceUpdateEvent,
    ProductStockUpdateEvent,
)
from pim_contracts.records import (
    AttributeGroup,
    AttributeSection,
    BundleRole,
    BundleRules,
    BundleTier,
    MasterBundleSetRecord,
    MasterBundleSetTranslation,
    MasterCategoryCompanion,
    MasterCategoryRecord,
    MasterCategoryTranslation,
    MasterCharacteristicRecord,
    MasterCharacteristicTranslation,
    MasterProductBundle,
    MasterProductPromo,
    MasterProductPromoTranslation,
    MasterProductRecord,
    MasterProductRelation,
    MasterProductTranslation,
    PartnerOfferRecord,
    PartnerProductRecord,
    RelationType,
    SearchHit,
    SearchMatch,
    SearchMode,
    SearchResponse,
    TranslationStatus,
)

# Версия пакета (pyproject.toml); SCHEMA_VERSION — отдельно, версия формата событий.
try:
    __version__ = _pkg_version("pim-contracts")
except PackageNotFoundError:  # запуск из исходников без установки
    __version__ = "0.0.0+unknown"

__all__ = [
    "PIM_EVENTS_EXCHANGE",
    "PIM_RAW_FEEDS_QUEUE",
    "ROUTING_KEY_FEED_ALL",
    "ROUTING_KEY_FEED_CANONICAL",
    "ROUTING_KEY_FEED_PRICE_UPDATE",
    "ROUTING_KEY_FEED_STOCK_UPDATE",
    "SCHEMA_VERSION",
    "AttributeGroup",
    "AttributeSection",
    "BaseEvent",
    "BundleRole",
    "BundleRules",
    "BundleTier",
    "CanonicalProductFeedEvent",
    "Currency",
    "EventType",
    "MasterBundleSetRecord",
    "MasterBundleSetTranslation",
    "MasterCategoryCompanion",
    "MasterCategoryRecord",
    "MasterCategoryTranslation",
    "MasterCharacteristicRecord",
    "MasterCharacteristicTranslation",
    "MasterProductBundle",
    "MasterProductPromo",
    "MasterProductPromoTranslation",
    "MasterProductRecord",
    "MasterProductRelation",
    "MasterProductTranslation",
    "PartnerOfferRecord",
    "PartnerProductRecord",
    "ProductPriceUpdateEvent",
    "ProductStockUpdateEvent",
    "RelationType",
    "SearchHit",
    "SearchMatch",
    "SearchMode",
    "SearchResponse",
    "SourceType",
    "TranslationStatus",
]
