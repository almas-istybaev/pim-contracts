import pytest
from pydantic import ValidationError

from pim_contracts import SearchHit, SearchResponse


def test_search_response_roundtrip():
    payload = {
        "query": "смеситель для кухни",
        "mode": "hybrid",
        "hits": [
            {"id": 7, "score": 0.031, "match": "hybrid"},
            {"id": 3, "score": 0.016, "match": "semantic"},
        ],
    }
    response = SearchResponse.model_validate(payload)
    assert [h.id for h in response.hits] == [7, 3]
    assert response.model_dump() == payload


def test_search_hit_rejects_unknown_match_and_negative_score():
    with pytest.raises(ValidationError):
        SearchHit.model_validate({"id": 1, "score": 0.1, "match": "fuzzy"})
    with pytest.raises(ValidationError):
        SearchHit.model_validate({"id": 1, "score": -1, "match": "lexical"})


def test_search_response_defaults_to_no_hits_and_ignores_extra():
    response = SearchResponse.model_validate({"query": "x", "mode": "lexical", "took_ms": 3})
    assert response.hits == []
