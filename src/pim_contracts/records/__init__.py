"""
Read-only master record DTOs served by inventory-monitor to storefront consumers.
"""
from pim_contracts.records.product import (
    MasterCategoryRecord,
    MasterCharacteristicRecord,
    MasterProductRecord,
)

__all__ = [
    "MasterCategoryRecord",
    "MasterCharacteristicRecord",
    "MasterProductRecord",
]
