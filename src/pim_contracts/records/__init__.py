"""
Read-only master record DTOs served by inventory to storefront consumers.
"""
from pim_contracts.records.product import (
    MasterCategoryRecord,
    MasterCategoryTranslation,
    MasterCharacteristicRecord,
    MasterCharacteristicTranslation,
    MasterProductRecord,
    MasterProductRelation,
    MasterProductTranslation,
)

__all__ = [
    "MasterCategoryRecord",
    "MasterCategoryTranslation",
    "MasterCharacteristicRecord",
    "MasterCharacteristicTranslation",
    "MasterProductRecord",
    "MasterProductRelation",
    "MasterProductTranslation",
]
