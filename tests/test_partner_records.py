from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from pim_contracts import (
    Currency,
    MasterProductRecord,
    PartnerOfferRecord,
    PartnerProductRecord,
)

RETAIL_FIELDS = {"price", "price_updated_at", "cost_price", "stock", "stock_quantity"}


def test_partner_product_fields_match_master_without_retail():
    master = MasterProductRecord.model_fields
    partner = PartnerProductRecord.model_fields
    assert list(partner) == [name for name in master if name not in RETAIL_FIELDS]
    for name, field in partner.items():
        assert field.annotation == master[name].annotation, name
        assert field.is_required() == master[name].is_required(), name
        assert field.default == master[name].default, name
        assert field.default_factory == master[name].default_factory, name


def test_master_product_field_order_unchanged():
    assert list(MasterProductRecord.model_fields) == [
        "id", "name", "slug", "previous_slugs", "mpn", "gpc_id", "brand",
        "shipping_weight", "shipping_length", "shipping_width", "shipping_height",
        "shipping_dimension_unit", "shipping_weight_unit", "category", "category_slug",
        "description", "seo_title", "seo_description", "characteristics",
        "price", "price_updated_at", "cost_price", "stock", "stock_quantity",
        "photos", "translations", "related",
    ]


def test_partner_product_from_master_payload_drops_retail():
    payload = {
        "id": 1,
        "name": "Смеситель",
        "slug": "smesitel",
        "category_slug": "smesiteli",
        "price": 12500.0,
        "cost_price": 9000.0,
        "stock": "в наличии",
        "stock_quantity": 4,
        "characteristics": [{"name": "Цвет", "value": "хром"}],
        "translations": {"kk": {"name": "Араластырғыш", "status": "machine"}},
        "related": [{"product_id": 2, "relation_type": "RECOMMENDED"}],
    }
    rec = PartnerProductRecord.model_validate(payload)
    dumped = rec.model_dump()
    assert not RETAIL_FIELDS & dumped.keys()
    assert dumped["slug"] == "smesitel"
    assert rec.characteristics[0].value == "хром"
    assert rec.related[0].product_id == 2


def test_partner_product_from_master_instance():
    master = MasterProductRecord(id=5, name="Унитаз", price=1.0, stock="нету", brand="Grohe")
    rec = PartnerProductRecord.model_validate(master.model_dump())
    assert rec.brand == "Grohe"
    assert rec.model_dump() == {k: v for k, v in master.model_dump().items() if k not in RETAIL_FIELDS}


def test_partner_offer_minimal_and_defaults():
    offer = PartnerOfferRecord(product_id=1, available_qty=0, lead_time_days=3)
    assert offer.wholesale_price is None
    assert offer.currency is Currency.KZT
    assert offer.updated_at is None


def test_partner_offer_roundtrip():
    offer = PartnerOfferRecord.model_validate(
        {
            "product_id": 7,
            "wholesale_price": 8400.5,
            "currency": "KZT",
            "available_qty": 12.0,
            "lead_time_days": 3,
            "updated_at": "2026-10-28T10:00:00Z",
            "future_field": "x",
        }
    )
    assert offer.updated_at == datetime(2026, 10, 28, 10, tzinfo=timezone.utc)
    assert PartnerOfferRecord.model_validate_json(offer.model_dump_json()) == offer
    assert offer.model_dump(mode="json")["currency"] == "KZT"


@pytest.mark.parametrize(
    "field,value",
    [("available_qty", -1), ("wholesale_price", -1), ("lead_time_days", -1), ("currency", "XXX")],
)
def test_partner_offer_rejects_invalid(field, value):
    data = {"product_id": 1, "available_qty": 1, "lead_time_days": 3, field: value}
    with pytest.raises(ValidationError):
        PartnerOfferRecord.model_validate(data)
