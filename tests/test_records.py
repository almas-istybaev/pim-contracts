from pim_contracts import (
    MasterCategoryRecord,
    MasterCategoryTranslation,
    MasterCharacteristicTranslation,
    MasterProductRecord,
    MasterProductRelation,
    MasterProductTranslation,
)
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
        "cost_price", "category_slug", "price_updated_at",
    ):
        assert getattr(rec, field) is None, field


def test_product_price_updated_at_parses_iso():
    rec = MasterProductRecord.model_validate(
        {"id": 5, "name": "Ванна", "price": 1.0, "stock": "в наличии",
         "price_updated_at": "2026-10-19T08:30:00Z"}
    )
    assert rec.price_updated_at is not None
    assert rec.price_updated_at.utcoffset() is not None
    assert rec.model_dump(mode="json")["price_updated_at"].startswith("2026-10-19T08:30:00")


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


def test_payload_1_4_0_without_slug_fields_is_valid():
    """Payload формата 1.4.0 (без slug/previous_slugs) остаётся валидным."""
    rec = MasterProductRecord.model_validate(
        {
            "id": 8, "name": "Унитаз", "price": 50.0, "stock": "в наличии",
            "category_slug": "unitazy", "seo_title": "Унитаз",
            "characteristics": [{"name": "Цвет", "value": "белый", "code": "color"}],
        }
    )
    assert rec.slug is None
    assert rec.previous_slugs == []


def test_product_slug_fields_roundtrip():
    rec = MasterProductRecord(
        id=9, name="Смеситель", price=1.0, stock="в наличии",
        slug="smesitel-grohe", previous_slugs=["smesitel", "smesitel-old"],
    )
    restored = MasterProductRecord.model_validate_json(rec.model_dump_json())
    assert restored == rec
    assert restored.previous_slugs == ["smesitel", "smesitel-old"]


def test_payload_1_5_0_without_translations_is_valid():
    """Payload формата 1.5.0 (без translations) остаётся валидным."""
    rec = MasterProductRecord.model_validate(
        {
            "id": 10, "name": "Ванна", "price": 90.0, "stock": "в наличии",
            "slug": "vanna-akril", "previous_slugs": ["vanna"],
        }
    )
    assert rec.translations == {}


def test_product_translations_roundtrip():
    rec = MasterProductRecord.model_validate(
        {
            "id": 11, "name": "Смеситель", "price": 1.0, "stock": "в наличии",
            "translations": {
                "kk": {"name": "Араластырғыш", "status": "reviewed", "extra": 1},
            },
        }
    )
    kk = rec.translations["kk"]
    assert isinstance(kk, MasterProductTranslation)
    assert kk.description is None
    assert kk.is_outdated is False
    restored = MasterProductRecord.model_validate_json(rec.model_dump_json())
    assert restored == rec


def test_translation_status_rejects_unknown_value():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        MasterProductTranslation(name="x", status="draft")


def test_payload_1_6_0_without_category_and_characteristic_translations_is_valid():
    """Payload формата 1.6.0 (без translations у категории и характеристик) остаётся валидным."""
    cat = MasterCategoryRecord.model_validate(
        {"id": 1, "name": "Смесители", "slug": "smesiteli", "parent_id": None}
    )
    assert cat.translations == {}
    rec = MasterProductRecord.model_validate(
        {
            "id": 12, "name": "Смеситель", "price": 1.0, "stock": "в наличии",
            "characteristics": [{"name": "Цвет", "value": "Хром", "code": "color"}],
            "translations": {"kk": {"name": "Араластырғыш", "status": "machine"}},
        }
    )
    assert rec.characteristics[0].translations == {}


def test_category_translations_roundtrip():
    cat = MasterCategoryRecord.model_validate(
        {
            "id": 2, "name": "Ванны", "slug": "vanny",
            "translations": {"kk": {"name": "Ванналар", "status": "machine", "extra": 1}},
        }
    )
    kk = cat.translations["kk"]
    assert isinstance(kk, MasterCategoryTranslation)
    assert kk.description is None
    assert kk.is_outdated is False
    restored = MasterCategoryRecord.model_validate_json(cat.model_dump_json())
    assert restored == cat


def test_characteristic_translations_roundtrip():
    rec = MasterCharacteristicRecord.model_validate(
        {
            "name": "Ширина", "value": "50 см", "code": "width", "unit": "см",
            "numeric_value": 50.0,
            "translations": {
                "kk": {
                    "name": "Ені", "value": "50 см", "unit": "см",
                    "status": "reviewed", "is_outdated": True,
                },
            },
        }
    )
    kk = rec.translations["kk"]
    assert isinstance(kk, MasterCharacteristicTranslation)
    assert kk.status == "reviewed"
    assert kk.is_outdated is True
    restored = MasterCharacteristicRecord.model_validate_json(rec.model_dump_json())
    assert restored == rec


def test_characteristic_translation_defaults():
    kk = MasterCharacteristicTranslation(status="machine")
    assert kk.name is None
    assert kk.value is None
    assert kk.unit is None
    assert kk.is_outdated is False


def test_category_and_characteristic_translation_status_rejects_unknown_value():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        MasterCategoryTranslation(name="x", status="draft")
    with pytest.raises(ValidationError):
        MasterCharacteristicTranslation(name="x", status="draft")
    with pytest.raises(ValidationError):
        MasterCategoryTranslation(name="x")


def test_payload_1_7_0_without_related_is_valid():
    """Payload формата 1.7.0 (без related) остаётся валидным."""
    rec = MasterProductRecord.model_validate({"id": 11, "name": "Раковина", "price": 50.0, "stock": "в наличии"})
    assert rec.related == []


def test_product_related_roundtrip():
    rec = MasterProductRecord.model_validate(
        {
            "id": 12, "name": "Раковина", "price": 50.0, "stock": "в наличии",
            "related": [
                {"product_id": 20, "relation_type": "REQUIRED_COMPONENT"},
                {"product_id": 21, "relation_type": "RECOMMENDED"},
            ],
        }
    )
    assert [(r.product_id, r.relation_type) for r in rec.related] == [(20, "REQUIRED_COMPONENT"), (21, "RECOMMENDED")]
    assert rec.model_dump()["related"][0] == {"product_id": 20, "relation_type": "REQUIRED_COMPONENT"}


def test_relation_type_rejects_unknown_value():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        MasterProductRelation(product_id=1, relation_type="ACCESSORY")


def test_payload_1_8_0_without_section_and_highlight_is_valid():
    """Payload формата 1.8.0 (характеристика без section/highlight) остаётся валидным."""
    ch = MasterCharacteristicRecord.model_validate({"name": "Ширина", "value": "30", "group": "base"})
    assert ch.section is None
    assert ch.highlight is None


def test_characteristic_section_and_highlight_roundtrip():
    for section in ("dimensions", "material", "installation", "features"):
        for highlight in (1, 4):
            ch = MasterCharacteristicRecord(name="a", value="b", section=section, highlight=highlight)
            restored = MasterCharacteristicRecord.model_validate_json(ch.model_dump_json())
            assert (restored.section, restored.highlight) == (section, highlight)


def test_characteristic_section_rejects_unknown_value():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        MasterCharacteristicRecord(name="a", value="b", section="other")


def test_characteristic_highlight_bounds():
    import pytest
    from pydantic import ValidationError

    for bad in (0, 5, -1):
        with pytest.raises(ValidationError):
            MasterCharacteristicRecord(name="a", value="b", highlight=bad)


def test_payload_1_9_0_without_values_is_valid():
    """Payload формата 1.9.0 (характеристика и перевод без values) остаётся валидным."""
    ch = MasterCharacteristicRecord.model_validate(
        {
            "name": "Функции",
            "value": "Антивандальная, Термостат",
            "translations": {"kk": {"value": "Вандалға қарсы, Термостат", "status": "machine"}},
        }
    )
    assert ch.values is None
    assert ch.translations["kk"].values is None


def test_characteristic_values_roundtrip():
    ch = MasterCharacteristicRecord.model_validate(
        {
            "name": "Функции",
            "value": "Антивандальная, Термостат",
            "values": ["Антивандальная", "Термостат"],
            "translations": {
                "kk": {"values": ["Вандалға қарсы", "Термостат"], "status": "reviewed"},
            },
        }
    )
    restored = MasterCharacteristicRecord.model_validate_json(ch.model_dump_json())
    assert restored.values == ["Антивандальная", "Термостат"]
    assert restored.translations["kk"].values == ["Вандалға қарсы", "Термостат"]


def test_category_payload_1_12_0_without_previous_slugs_is_valid():
    """Payload формата 1.12.0 (без previous_slugs) остаётся валидным."""
    cat = MasterCategoryRecord.model_validate({"id": 3, "name": "Ванны", "slug": "vanny"})
    assert cat.previous_slugs == []


def test_category_previous_slugs_roundtrip():
    cat = MasterCategoryRecord(
        id=4, name="Смесители", slug="smesiteli-dlya-vannoy", previous_slugs=["smesiteli", "smesiteli-old"]
    )
    assert cat.model_dump()["previous_slugs"] == ["smesiteli", "smesiteli-old"]
    restored = MasterCategoryRecord.model_validate_json(cat.model_dump_json())
    assert restored == cat
    assert restored.previous_slugs == ["smesiteli", "smesiteli-old"]
