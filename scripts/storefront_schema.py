"""
Writes schemas/storefront.schema.json — the JSON Schema of the records the storefront mirrors
(santeh24.kz frontend/src/lib/pim.ts). It ships in every vX.Y.Z tag; the storefront CI downloads
it by pinned version. tests/test_storefront_schema.py fails when the committed file is stale.

Run: .venv/bin/python scripts/storefront_schema.py
"""
import json
from pathlib import Path

import tomllib
from pydantic.json_schema import models_json_schema

from pim_contracts import (
    BundleRules,
    MasterBundleSetRecord,
    MasterCategoryRecord,
    MasterProductRecord,
    SearchResponse,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "schemas" / "storefront.schema.json"


def render() -> str:
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    _, schema = models_json_schema(
        [
            (MasterProductRecord, "serialization"),
            (MasterCategoryRecord, "serialization"),
            (BundleRules, "serialization"),
            (MasterBundleSetRecord, "serialization"),
            (SearchResponse, "serialization"),
        ],
        title="pim-contracts storefront records",
    )
    schema["x-pim-contracts-version"] = version
    return json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    OUT.write_text(render(), encoding="utf-8")
    print(f"-> {OUT.relative_to(ROOT)}")
