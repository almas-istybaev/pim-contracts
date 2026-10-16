"""
Read-only master record DTOs served by inventory to storefront consumers.
"""
from pim_contracts.records.product import (
    MasterCategoryRecord,
    MasterCharacteristicRecord,
    MasterProductRecord,
    MasterProductTranslation,
)

__all__ = [
    "MasterCategoryRecord",
    "MasterCharacteristicRecord",
    "MasterProductRecord",
    "MasterProductTranslation",
]
