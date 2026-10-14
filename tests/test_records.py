from pim_contracts import MasterCategoryRecord, MasterProductRecord
from pim_contracts.records import MasterCharacteristicRecord


def test_minimal_product_record_parses():
    rec = MasterProductRecord(id=1, name="Смеситель", price=12500.0, stock="в наличии")
    assert rec.id == 1
    assert rec.price == 12500.0
    assert rec.stock_quantity == 0.0
    assert rec.characteristics == []
    assert rec.photos == []


def test_product_unknown_extra_fields_ignored():
    rec = MasterProductRecord.model_validate(
        {"id": 2, "name": "Унитаз", "price": 1.0, "stock": "нету", "new_server_field": "x"}
    )
    assert not hasattr(rec, "new_server_field")
    assert "new_server_field" not in rec.model_dump()


def test_product_optional_fields_default_to_none():
    rec = MasterProductRecord(id=3, name="Раковина", price=5.0, stock="в наличии")
    for field in (
        "mpn", "gpc_id", "brand", "shipping_weight", "shipping_length",
        "shipping_width", "shipping_height", "category", "description",
        "cost_price", "category_slug",
    ):
        assert getattr(rec, field) is None, field


def test_product_characteristics_parse_nested():
    rec = MasterProductRecord.model_validate(
        {
            "id": 4, "name": "Душ", "price": 1.0, "stock": "в наличии",
            "characteristics": [{"name": "Материал", "value": "латунь", "extra": 1}],
        }
    )
    assert isinstance(rec.characteristics[0], MasterCharacteristicRecord)
    assert rec.characteristics[0].value == "латунь"


def test_minimal_category_record_parses_and_defaults():
    cat = MasterCategoryRecord(id=10, name="Смесители")
    assert cat.parent_id is None
    assert cat.description is None
    assert cat.photo is None
    assert cat.slug is None


def test_category_unknown_extra_fields_ignored():
    cat = MasterCategoryRecord.model_validate(
        {"id": 11, "name": "Ванны", "parent_id": 10, "slug": "vanny", "children": []}
    )
    assert cat.parent_id == 10
    assert cat.slug == "vanny"
    assert "children" not in cat.model_dump()


def test_slug_fields_parse():
    cat = MasterCategoryRecord(id=1, name="Смесители", slug="smesiteli")
    assert cat.slug == "smesiteli"
    rec = MasterProductRecord(id=1, name="X", price=1.0, stock="в наличии", category_slug="smesiteli")
    assert rec.category_slug == "smesiteli"
