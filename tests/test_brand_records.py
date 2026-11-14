import pytest
from pydantic import ValidationError

from pim_contracts import (
    MasterBrandPageRecord,
    MasterBrandPageTranslation,
    MasterProductRecord,
)

PAGE = {
    "brand": "Gloria",
    "brand_slug": "gloria",
    "category_slug": "kryuchki",
    "slug": "brand-gloria",
    "product_count": 90,
    "in_stock_count": 86,
    "price_min": 990.0,
    "price_max": 12500.0,
    "indexable": True,
    "h1": "Крючки Gloria",
    "seo_title": "Крючки Gloria — купить в Алматы",
    "seo_description": "86 моделей в наличии",
    "translations": {"kk": {"h1": "Gloria ілгектері"}},
}


def test_product_brand_slug_default_none_for_old_payload():
    rec = MasterProductRecord.model_validate({"id": 3, "name": "Ванна", "price": 1.0, "stock": "нету"})
    assert rec.brand_slug is None


def test_product_brand_slug_parses():
    rec = MasterProductRecord.model_validate(
        {"id": 3, "name": "Крючок", "price": 1.0, "stock": "нету", "brand": "Gloria", "brand_slug": "gloria"}
    )
    assert rec.brand_slug == "gloria"


def test_brand_page_parses_and_roundtrips():
    page = MasterBrandPageRecord.model_validate({**PAGE, "future_field": 1})
    assert page.previous_brand_slugs == []
    kk = page.translations["kk"]
    assert isinstance(kk, MasterBrandPageTranslation)
    assert kk.h1 == "Gloria ілгектері"
    assert kk.seo_title is None
    assert MasterBrandPageRecord.model_validate_json(page.model_dump_json()) == page


def test_brand_page_without_stock_is_not_indexable():
    page = MasterBrandPageRecord.model_validate(
        {**PAGE, "in_stock_count": 0, "price_min": None, "price_max": None, "indexable": False}
    )
    assert page.price_min is None
    assert page.indexable is False


@pytest.mark.parametrize("field", ["brand_slug", "category_slug", "slug", "indexable", "h1"])
def test_brand_page_required_fields(field):
    with pytest.raises(ValidationError):
        MasterBrandPageRecord.model_validate({k: v for k, v in PAGE.items() if k != field})


def test_brand_page_counts_not_negative():
    with pytest.raises(ValidationError):
        MasterBrandPageRecord.model_validate({**PAGE, "in_stock_count": -1})


def test_brand_page_stats_text_optional_since_1_29() -> None:
    from pim_contracts import MasterBrandPageRecord

    base = {
        "brand": "Gloria",
        "brand_slug": "gloria",
        "category_slug": "kryuchki",
        "slug": "brand-gloria",
        "product_count": 5,
        "in_stock_count": 4,
        "indexable": True,
        "h1": "Крючки Gloria",
    }
    assert MasterBrandPageRecord.model_validate(base).stats_text is None
    page = MasterBrandPageRecord.model_validate({**base, "stats_text": "x", "translations": {"kk": {"stats_text": "y"}}})
    assert page.stats_text == "x" and page.translations["kk"].stats_text == "y"
