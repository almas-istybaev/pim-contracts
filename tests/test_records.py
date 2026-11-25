import pytest
from pydantic import ValidationError

from pim_contracts import (
    MasterCategoryCompanion,
    MasterCategoryRecord,
    MasterCategoryTranslation,
    MasterCharacteristicTranslation,
    MasterProductPromo,
    MasterProductRecord,
    MasterProductRelation,
    MasterProductTranslation,
    MasterVariantGroup,
    ProductVideo,
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
        "cost_price", "category_slug", "price_updated_at", "content_updated_at",
        "out_of_stock_since",
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


def test_product_content_updated_at_parses_iso_and_old_payload_has_none():
    old = MasterProductRecord.model_validate({"id": 6, "name": "Ванна", "price": 1.0, "stock": "нету"})
    assert old.content_updated_at is None
    rec = MasterProductRecord.model_validate(
        {"id": 6, "name": "Ванна", "price": 1.0, "stock": "нету",
         "content_updated_at": "2026-11-16T05:00:00Z"}
    )
    assert rec.content_updated_at is not None
    assert rec.content_updated_at.utcoffset() is not None
    assert rec.model_dump(mode="json")["content_updated_at"].startswith("2026-11-16T05:00:00")


def test_product_out_of_stock_since_absent_in_1_34_0_payload():
    """Payload формата 1.34.0 (без out_of_stock_since) остаётся валидным."""
    old = MasterProductRecord.model_validate({"id": 7, "name": "Унитаз", "price": 1.0, "stock": "нету"})
    assert old.out_of_stock_since is None
    assert old.model_dump(mode="json")["out_of_stock_since"] is None


def test_product_out_of_stock_since_roundtrip():
    rec = MasterProductRecord.model_validate(
        {"id": 7, "name": "Унитаз", "price": 1.0, "stock": "нету", "stock_quantity": 0.0,
         "out_of_stock_since": "2026-10-20T04:15:00Z"}
    )
    assert rec.out_of_stock_since is not None
    assert rec.out_of_stock_since.utcoffset() is not None
    assert rec.model_dump(mode="json")["out_of_stock_since"].startswith("2026-10-20T04:15:00")
    assert MasterProductRecord.model_validate_json(rec.model_dump_json()) == rec


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


def test_payload_1_15_0_without_merged_ids_is_valid():
    """Payload формата 1.15.0 (без merged_ids) остаётся валидным."""
    rec = MasterProductRecord.model_validate(
        {"id": 12, "name": "Смеситель", "price": 1.0, "stock": "в наличии", "slug": "smesitel"}
    )
    assert rec.merged_ids == []


def test_product_merged_ids_roundtrip():
    rec = MasterProductRecord(
        id=13, name="Смеситель", price=1.0, stock="в наличии",
        slug="smesitel-grohe", previous_slugs=["smesitel-grohe-2"], merged_ids=[101, 102],
    )
    restored = MasterProductRecord.model_validate_json(rec.model_dump_json())
    assert restored == rec
    assert restored.merged_ids == [101, 102]


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
    assert rec.model_dump(exclude_defaults=True)["related"][0] == {"product_id": 20, "relation_type": "REQUIRED_COMPONENT"}


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


def test_payload_1_16_0_without_promo_is_valid():
    """Payload формата 1.16.0 (без promo) остаётся валидным."""
    rec = MasterProductRecord.model_validate(
        {"id": 14, "name": "Смеситель", "price": 1.0, "stock": "в наличии"}
    )
    assert rec.promo is None


def test_product_promo_roundtrip():
    rec = MasterProductRecord.model_validate({
        "id": 15, "name": "Смеситель", "price": 8500.0, "stock": "в наличии",
        "promo": {
            "type": "sale", "compare_at_price": 10000.0, "until": "2027-03-25T18:59:59Z",
            "name": "Наурыз", "slug": "nauryz-2027",
            "translations": {"kk": {"name": "Наурыз"}},
        },
    })
    restored = MasterProductRecord.model_validate_json(rec.model_dump_json())
    assert restored == rec
    assert restored.promo is not None
    assert restored.promo.compare_at_price == 10000.0
    assert restored.promo.until is not None and restored.promo.until.utcoffset() is not None
    assert restored.promo.translations["kk"].name == "Наурыз"


def test_promo_clearance_defaults():
    promo = MasterProductPromo(type="clearance", compare_at_price=5000.0, note="повреждена упаковка")
    assert promo.until is None
    assert promo.name is None and promo.slug is None
    assert promo.translations == {}


def test_promo_starts_at_absent_in_1_33_0_payload():
    """Payload формата 1.33.0 (promo без starts_at) остаётся валидным."""
    promo = MasterProductPromo.model_validate(
        {"type": "sale", "compare_at_price": 10000.0, "until": "2027-03-25T18:59:59Z"}
    )
    assert promo.starts_at is None


def test_promo_starts_at_roundtrip():
    rec = MasterProductRecord.model_validate({
        "id": 16, "name": "Смеситель", "price": 8500.0, "stock": "в наличии",
        "promo": {
            "type": "sale", "compare_at_price": 10000.0,
            "starts_at": "2027-03-14T19:00:00Z", "until": "2027-03-25T18:59:59Z",
        },
    })
    restored = MasterProductRecord.model_validate_json(rec.model_dump_json())
    assert restored == rec
    assert restored.promo.starts_at is not None and restored.promo.starts_at.utcoffset() is not None
    assert restored.promo.starts_at < restored.promo.until


def test_promo_type_accepts_unknown_value():
    """Новые виды акций не ломают старых потребителей."""
    assert MasterProductPromo(type="flash", compare_at_price=2.0).type == "flash"


def test_category_cutout_absent_in_1_19_0_payload():
    """Payload формата 1.19.0 (без cutout) остаётся валидным."""
    cat = MasterCategoryRecord.model_validate({"id": 1, "name": "Унитазы", "photo": "https://cdn/x.jpg"})
    assert cat.cutout is None


def test_category_cutout_roundtrip():
    cat = MasterCategoryRecord.model_validate(
        {"id": 2, "name": "Смесители", "cutout": "https://cdn.santeh24.kz/categories/smesiteli.webp"}
    )
    restored = MasterCategoryRecord.model_validate_json(cat.model_dump_json())
    assert restored.cutout == "https://cdn.santeh24.kz/categories/smesiteli.webp"


def test_relation_absent_new_fields_in_1_20_0_payload():
    """Связь формата 1.20.0 (без kind/score/reason) остаётся валидной."""
    rel = MasterProductRelation.model_validate({"product_id": 5, "relation_type": "RECOMMENDED"})
    assert rel.kind is None and rel.score is None and rel.reason == []


def test_relation_rule_fields_roundtrip():
    rel = MasterProductRelation.model_validate(
        {
            "product_id": 7,
            "relation_type": "REQUIRED_COMPONENT",
            "kind": "rule",
            "score": 0.82,
            "reason": ["same_width", "future_code"],
        }
    )
    restored = MasterProductRelation.model_validate_json(rel.model_dump_json())
    assert restored.kind == "rule" and restored.score == 0.82
    assert restored.reason == ["same_width", "future_code"]


def test_relation_score_bounds():
    with pytest.raises(ValidationError):
        MasterProductRelation(product_id=1, relation_type="RECOMMENDED", score=1.5)


def test_category_companions_absent_in_1_20_0_payload():
    cat = MasterCategoryRecord.model_validate({"id": 1, "name": "Тумбы"})
    assert cat.companions == [] and cat.substitute_group is None


def test_category_companions_roundtrip():
    cat = MasterCategoryRecord.model_validate(
        {
            "id": 10,
            "name": "Тумбы под раковину",
            "substitute_group": "furniture",
            "companions": [
                {"category_id": 21, "category_slug": "na-tumbu", "relation_type": "REQUIRED_COMPONENT", "priority": 1},
                {"category_id": 30, "relation_type": "RECOMMENDED", "priority": 4},
            ],
        }
    )
    restored = MasterCategoryRecord.model_validate_json(cat.model_dump_json())
    assert [c.category_id for c in restored.companions] == [21, 30]
    assert restored.companions[1].category_slug is None
    assert restored.substitute_group == "furniture"


def test_category_companion_priority_positive():
    with pytest.raises(ValidationError):
        MasterCategoryCompanion(category_id=1, relation_type="RECOMMENDED", priority=0)


def test_product_videos_default_empty_for_old_payload():
    rec = MasterProductRecord.model_validate({"id": 3, "name": "Ванна", "price": 1.0, "stock": "нету"})
    assert rec.videos == []


def test_product_videos_parse():
    rec = MasterProductRecord.model_validate(
        {
            "id": 4,
            "name": "Унитаз",
            "price": 1.0,
            "stock": "в наличии",
            "videos": [
                {
                    "url": "https://cdn.santeh24.kz/videos/4/review.mp4",
                    "poster": "https://cdn.santeh24.kz/videos/4/review.jpg",
                    "duration_sec": 42,
                    "width": 720,
                    "height": 1280,
                    "uploaded_at": "2026-11-10T10:00:00Z",
                }
            ],
        }
    )
    video = rec.videos[0]
    assert isinstance(video, ProductVideo)
    assert video.height > video.width
    assert video.title is None


def test_product_video_requires_url_and_poster():
    with pytest.raises(ValidationError):
        ProductVideo.model_validate({"url": "https://cdn.santeh24.kz/v.mp4"})


def test_product_sort_rank_default_none_for_old_payload():
    rec = MasterProductRecord.model_validate({"id": 3, "name": "Ванна", "price": 1.0, "stock": "нету"})
    assert rec.sort_rank is None


def test_product_sort_rank_not_negative():
    rec = MasterProductRecord.model_validate({"id": 3, "name": "Ванна", "price": 1.0, "stock": "нету", "sort_rank": 2})
    assert rec.sort_rank == 2
    with pytest.raises(ValidationError):
        MasterProductRecord.model_validate({"id": 3, "name": "Ванна", "price": 1.0, "stock": "нету", "sort_rank": -1})


def test_product_variant_group_default_none_for_old_payload():
    rec = MasterProductRecord.model_validate({"id": 3, "name": "Ванна", "price": 1.0, "stock": "нету"})
    assert rec.variant_group is None


def test_product_variant_group_parses_and_roundtrips():
    rec = MasterProductRecord.model_validate(
        {
            "id": 10,
            "name": "Ванна акриловая 170×70 левая",
            "price": 1.0,
            "stock": "в наличии",
            "variant_group": {
                "id": 7,
                "axes": [
                    {"code": "size", "label": "Размер", "label_kk": "Өлшемі"},
                    {"code": "side", "label": "Сторона"},
                ],
                "members": [
                    {
                        "product_id": 10,
                        "slug": "vanna-170-70-levaya",
                        "values": {"size": "170×70", "side": "Левая"},
                        "values_kk": {"side": "Сол жақ"},
                    },
                    {"product_id": 11, "values": {"size": "170×70", "side": "Правая"}},
                ],
            },
        }
    )
    group = rec.variant_group
    assert isinstance(group, MasterVariantGroup)
    assert [a.code for a in group.axes] == ["size", "side"]
    assert group.axes[1].label_kk is None
    assert group.members[1].slug is None
    assert group.members[1].values_kk == {}
    restored = MasterProductRecord.model_validate_json(rec.model_dump_json())
    assert restored.variant_group == group


def test_variant_group_unknown_axis_does_not_break():
    group = MasterVariantGroup.model_validate(
        {
            "id": 1,
            "axes": [{"code": "foo", "label": "Что-то новое", "future_field": 1}],
            "members": [
                {"product_id": 1, "values": {"foo": "a"}},
                {"product_id": 2, "values": {"foo": "b"}},
            ],
        }
    )
    assert group.axes[0].code == "foo"
    assert [m.values["foo"] for m in group.members] == ["a", "b"]


def test_category_stats_optional_since_1_29() -> None:
    from pim_contracts import MasterCategoryRecord

    old = MasterCategoryRecord.model_validate({"id": 1, "name": "Тумбы"})
    assert old.stats is None and old.stats_text is None
    new = MasterCategoryRecord.model_validate(
        {
            "id": 1,
            "name": "Тумбы",
            "stats": {"product_count": 12, "in_stock_count": 8, "price_min": 25900, "price_max": 89000},
            "stats_text": "В каталоге 12 моделей.",
            "translations": {"kk": {"status": "reviewed", "stats_text": "Каталогта 12 модель."}},
        }
    )
    assert new.stats is not None and new.stats.in_stock_count == 8
    assert new.translations["kk"].stats_text == "Каталогта 12 модель."


def test_category_faq_optional_since_1_30() -> None:
    old = MasterCategoryRecord.model_validate(
        {"id": 1, "name": "Тумбы", "translations": {"kk": {"status": "reviewed", "name": "Тумбалар"}}}
    )
    assert old.faq == [] and old.translations["kk"].faq == []
    new = MasterCategoryRecord.model_validate(
        {
            "id": 1,
            "name": "Тумбы",
            "faq": [{"question": "Сколько стоит?", "answer": "От 18 000 до 193 200 ₸.", "future": 1}],
            "translations": {
                "kk": {"status": "reviewed", "faq": [{"question": "Қанша тұрады?", "answer": "18 000 ₸-ден."}]}
            },
        }
    )
    assert new.faq[0].question == "Сколько стоит?"
    assert new.translations["kk"].faq[0].answer == "18 000 ₸-ден."
    with pytest.raises(ValidationError):
        MasterCategoryRecord.model_validate({"id": 1, "name": "Тумбы", "faq": [{"question": "Без ответа"}]})


def test_product_questions_optional_since_1_31() -> None:
    old = MasterProductRecord.model_validate({"id": 1, "name": "Смеситель", "price": 12500.0, "stock": "в наличии"})
    assert old.questions == []
    new = MasterProductRecord.model_validate(
        {
            "id": 1,
            "name": "Смеситель",
            "price": 12500.0,
            "stock": "в наличии",
            "questions": [
                {
                    "id": 7,
                    "question": "Подходит к раковине с одним отверстием?",
                    "answer": "Да, монтаж в одно отверстие.",
                    "answered_at": "2026-11-10T08:30:00Z",
                    "translations": {
                        "kk": {"question": "Бір тесікке келе ме?", "answer": "Иә.", "status": "machine"}
                    },
                    "future": 1,
                }
            ],
        }
    )
    q = new.questions[0]
    assert q.id == 7 and q.answered_at.year == 2026
    assert q.translations["kk"].status == "machine"
    with pytest.raises(ValidationError):
        MasterProductRecord.model_validate(
            {"id": 1, "name": "Смеситель", "price": 1.0, "stock": "x", "questions": [{"id": 1, "question": "?"}]}
        )


def test_category_kit_categories_optional_since_1_31() -> None:
    old = MasterCategoryRecord.model_validate({"id": 1, "name": "Унитазы"})
    assert old.kit_categories == []
    new = MasterCategoryRecord.model_validate(
        {
            "id": 1,
            "name": "Унитазы",
            "kit_categories": [
                {
                    "category_id": 5,
                    "slug": "installyacii",
                    "name": "Инсталляции",
                    "translations": {"kk": {"name": "Инсталляциялар"}},
                    "price_min": 45900,
                    "important": True,
                },
                {"category_id": 6, "slug": "sidenya", "name": "Сиденья", "price_min": 9900},
            ],
        }
    )
    kit = new.kit_categories
    assert kit[0].important is True and kit[0].translations["kk"].name == "Инсталляциялар"
    assert kit[1].important is False and kit[1].translations == {}
    with pytest.raises(ValidationError):
        MasterCategoryRecord.model_validate(
            {"id": 1, "name": "Унитазы", "kit_categories": [{"category_id": 5, "slug": "s", "name": "n", "price_min": 0}]}
        )


def test_category_sort_order_optional_since_1_32() -> None:
    assert MasterCategoryRecord.model_validate({"id": 1, "name": "Душевые"}).sort_order is None
    assert MasterCategoryRecord.model_validate({"id": 1, "name": "Душевые", "sort_order": 10}).sort_order == 10
