from pim_contracts import MasterCategoryRecord, MasterProductRecord


def test_old_payloads_without_listing_fields_validate():
    product = MasterProductRecord.model_validate({"id": 1, "name": "Ванна", "price": 1.0, "stock": "нету"})
    category = MasterCategoryRecord.model_validate({"id": 5, "name": "Ванны"})
    assert product.size_label is None
    assert category.filter_order == []


def test_listing_fields_parse():
    product = MasterProductRecord.model_validate(
        {"id": 1, "name": "Ванна", "price": 1.0, "stock": "нету", "size_label": "170×70 см"}
    )
    category = MasterCategoryRecord.model_validate(
        {"id": 5, "name": "Ванны", "filter_order": ["bath_length", "width", "price"]}
    )
    assert product.size_label == "170×70 см"
    assert category.filter_order == ["bath_length", "width", "price"]
