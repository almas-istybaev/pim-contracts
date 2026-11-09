"""
Product search DTOs served by inventory to storefronts (since 1.22.0).

Inventory ranks the products (lexical match with Russian morphology and typo tolerance plus
semantic vector match); the storefront renders the hits from its own cache in the given order and
drops ids it does not have. Consumers: santeh24.kz frontend/src/lib/pim.ts.
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SearchMatch = Literal["exact", "lexical", "semantic", "hybrid"]
SearchMode = Literal["hybrid", "lexical"]


class SearchHit(BaseModel):
    """One ranked product of a search response (since 1.22.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    id: int = Field(..., description="MasterProductRecord.id")
    score: float = Field(..., ge=0, description="Relevance, higher is better; comparable only within one response")
    match: SearchMatch = Field(
        ...,
        description=(
            "Why the product was found: exact — SKU / article; lexical — words of the query; "
            "semantic — meaning only (synonyms, other language); hybrid — both"
        ),
    )


class SearchResponse(BaseModel):
    """Ranked search result (since 1.22.0)."""

    model_config = ConfigDict(extra="ignore", from_attributes=True)

    query: str = Field(..., description="The query as received")
    mode: SearchMode = Field(
        ...,
        description="hybrid — words and meaning; lexical — words only (semantic part unavailable or not needed)",
    )
    hits: list[SearchHit] = Field(default_factory=list, description="Best first")
