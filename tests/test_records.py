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


def test_characteristic_new_fields_default_to_none():
    ch = MasterCharacteristicRecord(name="Ширина", value="30")
    assert ch.code is None
    assert ch.group is None
    assert ch.unit is None
    assert ch.numeric_value is None


def test_characteristic_new_fields_roundtrip():
    ch = MasterCharacteristicRecord(
        name="Ширина", value="30", code="width", group="base", unit="cm", numeric_value=30.0
    )
    restored = MasterCharacteristicRecord.model_validate_json(ch.model_dump_json())
    assert restored == ch
    assert restored.group == "base"
    assert restored.numeric_value == 30.0


def test_characteristic_group_rejects_unknown_value():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        MasterCharacteristicRecord(name="a", value="b", group="other")


def test_product_new_fields_default_to_none():
    rec = MasterProductRecord(id=5, name="Кран", price=1.0, stock="в наличии")
    for field in ("shipping_dimension_unit", "shipping_weight_unit", "seo_title", "seo_description"):
        assert getattr(rec, field) is None, field


def test_old_payload_without_new_fields_is_valid():
    """Payload формата 1.3.x (без новых полей 1.4.0) остаётся валидным."""
    rec = MasterProductRecord.model_validate(
        {
            "id": 6, "name": "Мойка", "price": 10.0, "stock": "в наличии",
            "shipping_weight": "2", "category_slug": "moyki",
            "characteristics": [{"name": "Материал", "value": "сталь"}],
        }
    )
    assert rec.characteristics[0].code is None
    assert rec.shipping_weight_unit is None
    assert rec.seo_title is None


def test_product_new_fields_roundtrip():
    rec = MasterProductRecord(
        id=7, name="Смеситель", price=1.0, stock="в наличии",
        shipping_weight="1.5", shipping_weight_unit="kg",
        shipping_length="10", shipping_width="5", shipping_height="20",
        shipping_dimension_unit="cm",
        seo_title="Смеситель — купить в Алматы", seo_description="Описание",
        characteristics=[
            {"name": "Цвет", "value": "хром", "code": "color", "group": "category"},
            {"name": "Ширина", "value": "30", "code": "width", "unit": "cm", "numeric_value": 30},
        ],
    )
    restored = MasterProductRecord.model_validate_json(rec.model_dump_json())
    assert restored == rec
    assert restored.characteristics[1].numeric_value == 30.0
    assert restored.shipping_dimension_unit == "cm"
