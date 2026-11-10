import pytest
from pydantic import ValidationError

from pim_contracts import ServiceSummary, SummaryItem, SummaryStatus


def test_service_summary_roundtrip():
    payload = {
        "service": "inventory",
        "version": "2.64.2",
        "generated_at": "2026-11-10T09:00:00+05:00",
        "items": [
            {
                "key": "drafts",
                "label": "Черновики",
                "value": 38,
                "level": "info",
                "url": "https://pim.santeh24.kz/?public=false",
            }
        ],
        "status": [
            {
                "key": "feed",
                "label": "Последнее событие фида",
                "level": "ok",
                "at": "2026-11-10T08:48:00+05:00",
                "value": None,
            }
        ],
    }
    summary = ServiceSummary.model_validate(payload)
    assert summary.items[0].value == 38
    assert summary.status[0].at is not None and summary.status[0].at.utcoffset() is not None
    assert ServiceSummary.model_validate_json(summary.model_dump_json()) == summary


def test_minimal_summary_and_defaults():
    summary = ServiceSummary.model_validate(
        {"service": "instagram", "version": "0.2.0", "generated_at": "2026-11-10T04:00:00Z", "uptime": 1}
    )
    assert summary.items == [] and summary.status == []
    assert SummaryItem(key="wait", label="Без ответа", value=4).level == "info"
    assert SummaryStatus(key="token", label="Токен Instagram", value="40 дней").level == "ok"


def test_rejects_unknown_level_and_empty_key():
    with pytest.raises(ValidationError):
        SummaryItem.model_validate({"key": "x", "label": "X", "value": 1, "level": "critical"})
    with pytest.raises(ValidationError):
        SummaryStatus.model_validate({"key": "", "label": "X"})
