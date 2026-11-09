"""
Read-only master record DTOs served by inventory to storefront consumers.
"""
from pim_contracts.records.bundle import (
    BundleRole,
    BundleRules,
    BundleTier,
    MasterBundleSetRecord,
    MasterBundleSetTranslation,
)
from pim_contracts.records.partner import PartnerOfferRecord, PartnerProductRecord
from pim_contracts.records.product import (
    AttributeGroup,
    AttributeSection,
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
    RelationType,
    TranslationStatus,
)
from pim_contracts.records.search import SearchHit, SearchMatch, SearchMode, SearchResponse

__all__ = [
    "AttributeGroup",
    "AttributeSection",
    "BundleRole",
    "BundleRules",
    "BundleTier",
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
    "RelationType",
    "SearchHit",
    "SearchMatch",
    "SearchMode",
    "SearchResponse",
    "TranslationStatus",
]
