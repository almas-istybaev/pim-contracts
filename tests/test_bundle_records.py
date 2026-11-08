import pytest
from pydantic import ValidationError

from pim_contracts import (
    BundleRole,
    BundleRules,
    BundleTier,
    MasterBundleSetRecord,
    MasterCategoryRecord,
    MasterProductBundle,
    MasterProductRecord,
    PartnerProductRecord,
)

RULES_PAYLOAD = {
    "enabled": True,
    "tiers": [
        {"roles": 2, "percent": 3},
        {"roles": 3, "percent": 5},
        {"roles": 4, "percent": 7},
    ],
    "roles": [
        {"key": "bath", "name": "Ванна или душ", "name_kk": "Ванна немесе душ", "min_price": 50000},
        {"key": "toilet", "name": "Унитаз", "name_kk": "Унитаз", "min_price": 30000},
        {"key": "furniture", "name": "Мебель", "min_price": 30000},
        {"key": "mirror", "name": "Зеркало", "min_price": 15000},
        {"key": "mixer", "name": "Смеситель", "min_price": 15000},
        {"key": "sink", "name": "Раковина", "min_price": 15000},
    ],
}


def test_payload_1_18_0_without_bundle_is_valid():
    """Payload формата 1.18.0 (без bundle / bundle_role) остаётся валидным."""
    product = MasterProductRecord.model_validate(
        {"id": 1, "name": "Смеситель", "price": 1.0, "stock": "в наличии"}
    )
    assert product.bundle is None
    category = MasterCategoryRecord.model_validate({"id": 1, "name": "Смесители"})
    assert category.bundle_role is None


def test_product_bundle_roundtrip():
    rec = MasterProductRecord.model_validate({
        "id": 2, "name": "Унитаз", "price": 45000.0, "stock": "в наличии",
        "bundle": {"role": "toilet", "max_percent": 7},
    })
    restored = MasterProductRecord.model_validate_json(rec.model_dump_json())
    assert restored.bundle == MasterProductBundle(role="toilet", max_percent=7)


def test_product_bundle_accessory_and_unknown_role():
    """Нет роли = аксессуар; неизвестный ключ роли не ломает валидацию."""
    assert MasterProductBundle(max_percent=5).role is None
    assert MasterProductBundle(role="bidet", max_percent=0).role == "bidet"


@pytest.mark.parametrize("value", [-1, 101])
def test_product_bundle_max_percent_bounds(value):
    with pytest.raises(ValidationError):
        MasterProductBundle(role="sink", max_percent=value)


def test_product_bundle_max_percent_required():
    with pytest.raises(ValidationError):
        MasterProductBundle.model_validate({"role": "sink"})


def test_category_bundle_role_roundtrip():
    cat = MasterCategoryRecord.model_validate({"id": 3, "name": "Ванны", "bundle_role": "bath"})
    assert MasterCategoryRecord.model_validate_json(cat.model_dump_json()).bundle_role == "bath"


def test_bundle_rules_roundtrip():
    rules = BundleRules.model_validate(RULES_PAYLOAD)
    restored = BundleRules.model_validate_json(rules.model_dump_json())
    assert restored == rules
    assert [t.percent for t in restored.tiers] == [3, 5, 7]
    assert restored.roles[2].name_kk is None
    assert restored.roles[0].min_price == 50000


def test_bundle_rules_defaults_disabled():
    rules = BundleRules()
    assert rules.enabled is False
    assert rules.tiers == [] and rules.roles == []


def test_bundle_rules_ignore_extra_fields():
    rules = BundleRules.model_validate({**RULES_PAYLOAD, "future": 1})
    assert rules.enabled is True


@pytest.mark.parametrize("payload", [
    {"roles": 0, "percent": 3},
    {"roles": 2, "percent": -1},
    {"roles": 2, "percent": 101},
])
def test_bundle_tier_bounds(payload):
    with pytest.raises(ValidationError):
        BundleTier.model_validate(payload)


def test_bundle_role_min_price_non_negative():
    with pytest.raises(ValidationError):
        BundleRole(key="sink", name="Раковина", min_price=-1)


def test_bundle_set_roundtrip():
    rec = MasterBundleSetRecord.model_validate({
        "slug": "komplekt-vannaya-classic",
        "name": "Ванная Classic",
        "translations": {"kk": {"name": "Classic жуынатын бөлмесі"}},
        "image": "https://cdn.santeh24.kz/sets/classic.jpg",
        "product_ids": [10, 11, 12],
    })
    restored = MasterBundleSetRecord.model_validate_json(rec.model_dump_json())
    assert restored == rec
    assert restored.translations["kk"].name == "Classic жуынатын бөлмесі"


def test_bundle_set_minimal():
    rec = MasterBundleSetRecord(slug="s", name="Набор")
    assert rec.image is None and rec.product_ids == [] and rec.translations == {}


def test_partner_product_drops_bundle():
    """bundle — розничные данные (max_percent от маржи), партнёрам не отдаются."""
    partner = PartnerProductRecord.model_validate({
        "id": 1, "name": "Унитаз", "bundle": {"role": "toilet", "max_percent": 7},
    })
    assert "bundle" not in partner.model_dump()
