import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from pim_contracts import (
    PIM_EVENTS_EXCHANGE,
    PIM_RAW_FEEDS_QUEUE,
    ROUTING_KEY_FEED_CANONICAL,
    Currency,
    SourceType,
)
from pim_contracts.events import (
    BaseEvent,
    CanonicalProductFeedEvent,
    ProductPriceUpdateEvent,
    ProductStockUpdateEvent,
)


def test_amqp_constants():
    assert PIM_EVENTS_EXCHANGE == "pim.events"
    assert PIM_RAW_FEEDS_QUEUE == "pim_raw_feeds"
    assert ROUTING_KEY_FEED_CANONICAL == "pim.feed.canonical"


def test_base_event_defaults():
    event = BaseEvent()
    assert isinstance(event.event_id, uuid.UUID)
    assert event.schema_version == "1.0.0"
    assert event.occurred_at is not None
    assert event.trace_id is None


def test_canonical_feed_event_roundtrip_serialization():
    price_dec = Decimal("48500.50")
    event = CanonicalProductFeedEvent(
        supplier_id="adi-ceramic-mysklad",
        supplier_sku="ART-1002",
        normalized_mpn="ART1002",
        name="Тумба с умывальником 60",
        description="Влагостойкая МДФ",
        attributes={"physical_stock": "10", "reserve": "2"},
        raw_price=price_dec,
        stock=8,
        currency=Currency.KZT,
        source_channel=SourceType.MOYSKLAD_API,
        payload_hash="e3b0c44298fc1c149afbf4c8996fb924",
    )

    # Serialize to JSON string
    json_str = event.model_dump_json()
    data = json.loads(json_str)

    assert data["supplier_id"] == "adi-ceramic-mysklad"
    assert data["stock"] == 8
    assert data["currency"] == "KZT"
    assert data["source_channel"] == "moysklad_api"

    # Deserialize back from JSON
    parsed = CanonicalProductFeedEvent.model_validate_json(json_str)
    assert parsed.supplier_sku == "ART-1002"
    assert parsed.raw_price == price_dec
    assert parsed.event_id == event.event_id
    assert parsed.schema_version == "1.0.0"


def test_forward_compatibility_extra_fields_ignored():
    """
    Law of Robustness (Postel's Law): Consumer MUST ignore unknown future fields
    added by newer producer versions without raising ValidationError.
    """
    payload_with_future_fields = {
        "supplier_id": "supp_test",
        "supplier_sku": "SKU_FUTURE",
        "normalized_mpn": "SKUFUTURE",
        "name": "Товар из будущего",
        "raw_price": "12000.00",
        "stock": 5,
        "source_channel": "moysklad_api",
        "payload_hash": "dummy_hash",
        # Unknown fields from v1.2+
        "future_ai_tag": "modern_loft",
        "warranty_months": 24,
        "carbon_footprint_kg": 1.2,
    }

    parsed = CanonicalProductFeedEvent.model_validate(payload_with_future_fields)
    assert parsed.supplier_sku == "SKU_FUTURE"
    assert parsed.raw_price == Decimal("12000.00")
    assert not hasattr(parsed, "future_ai_tag")


def test_stock_update_event():
    event = ProductStockUpdateEvent(
        supplier_id="supp_test",
        supplier_sku="SKU_1",
        normalized_mpn="SKU1",
        raw_price=Decimal("15000.00"),
        stock=0,
        payload_hash="hash_zeroed",
        reason="absent_from_sitemap",
    )
    assert event.stock == 0
    assert event.reason == "absent_from_sitemap"
    json_data = json.loads(event.model_dump_json())
    assert json_data["reason"] == "absent_from_sitemap"


@pytest.mark.parametrize("event_cls", [CanonicalProductFeedEvent, ProductStockUpdateEvent])
def test_supplier_retail_fields_roundtrip(event_cls):
    """1.15.0: розница поставщика с его сайта — отдельно от raw_price."""
    kwargs = {"supplier_id": "gloria", "supplier_sku": "G-1", "raw_price": Decimal("40000.00")}
    if event_cls is CanonicalProductFeedEvent:
        kwargs["name"] = "Смеситель"
    observed = datetime(2026, 10, 29, 6, 30, tzinfo=timezone.utc)
    event = event_cls(
        **kwargs,
        supplier_retail_price=Decimal("52990.00"),
        supplier_retail_source="site",
        supplier_retail_observed_at=observed,
    )
    parsed = event_cls.model_validate_json(event.model_dump_json())
    assert parsed.supplier_retail_price == Decimal("52990.00")
    assert parsed.raw_price == Decimal("40000.00")
    assert parsed.supplier_retail_source == "site"
    assert parsed.supplier_retail_observed_at == observed

    with pytest.raises(ValidationError):
        event_cls(**kwargs, supplier_retail_price=Decimal("-1"))


@pytest.mark.parametrize("event_cls", [CanonicalProductFeedEvent, ProductStockUpdateEvent])
def test_supplier_retail_fields_absent_in_old_payload(event_cls):
    """Payload ≤1.14.0 без новых полей валиден, поля = None (неизвестно)."""
    payload = {"supplier_id": "gloria", "supplier_sku": "G-1", "raw_price": "40000.00"}
    if event_cls is CanonicalProductFeedEvent:
        payload["name"] = "Смеситель"
    parsed = event_cls.model_validate_json(json.dumps(payload))
    assert parsed.supplier_retail_price is None
    assert parsed.supplier_retail_source is None
    assert parsed.supplier_retail_observed_at is None
    assert json.loads(parsed.model_dump_json())["supplier_retail_price"] is None


def test_price_update_event():
    event = ProductPriceUpdateEvent(
        supplier_id="supp_test",
        supplier_sku="SKU_1",
        normalized_mpn="SKU1",
        old_price=Decimal("10000.00"),
        new_price=Decimal("11500.00"),
        payload_hash="hash_price",
    )
    assert event.old_price == Decimal("10000.00")
    assert event.new_price == Decimal("11500.00")


def test_json_schema_generation():
    schema = CanonicalProductFeedEvent.model_json_schema()
    assert schema["type"] == "object"
    assert "supplier_sku" in schema["properties"]
    assert "stock" in schema["properties"]
    assert "raw_price" in schema["properties"]


def test_package_version_matches_pyproject():
    """__version__ — версия пакета, а не SCHEMA_VERSION формата событий."""
    from pathlib import Path

    import tomllib

    import pim_contracts

    pyproject = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
    assert pim_contracts.__version__ == pyproject["project"]["version"]


def test_literal_types_exported_and_used_by_records():
    """Именованные Literal-типы доступны потребителям и совпадают с полями записей (с 1.12.0)."""
    from typing import get_args

    from pim_contracts import (
        AttributeGroup,
        AttributeSection,
        MasterCharacteristicRecord,
        MasterProductRelation,
        MasterProductTranslation,
        RelationType,
        TranslationStatus,
    )

    assert get_args(TranslationStatus) == ("machine", "reviewed")
    assert MasterProductTranslation.model_fields["status"].annotation == TranslationStatus
    assert MasterProductRelation.model_fields["relation_type"].annotation == RelationType
    assert MasterCharacteristicRecord.model_fields["group"].annotation == AttributeGroup | None
    assert MasterCharacteristicRecord.model_fields["section"].annotation == AttributeSection | None
