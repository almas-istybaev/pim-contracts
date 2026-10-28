"""
Read-only master record DTOs served by inventory to storefront consumers.
"""
from pim_contracts.records.product import (
    AttributeGroup,
    AttributeSection,
    MasterCategoryRecord,
    MasterCategoryTranslation,
    MasterCharacteristicRecord,
    MasterCharacteristicTranslation,
    MasterProductRecord,
    MasterProductRelation,
    MasterProductTranslation,
    RelationType,
    TranslationStatus,
)
from pim_contracts.records.partner import PartnerOfferRecord, PartnerProductRecord

__all__ = [
    "AttributeGroup",
    "AttributeSection",
    "MasterCategoryRecord",
    "MasterCategoryTranslation",
    "MasterCharacteristicRecord",
    "MasterCharacteristicTranslation",
    "MasterProductRecord",
    "MasterProductRelation",
    "MasterProductTranslation",
    "PartnerOfferRecord",
    "PartnerProductRecord",
    "RelationType",
    "TranslationStatus",
]
