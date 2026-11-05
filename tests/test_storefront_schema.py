import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "storefront_schema.py"
_spec = importlib.util.spec_from_file_location("storefront_schema", _SCRIPT)
storefront_schema = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(storefront_schema)


def test_committed_storefront_schema_is_current():
    assert storefront_schema.OUT.read_text(encoding="utf-8") == storefront_schema.render(), (
        "schemas/storefront.schema.json устарел: .venv/bin/python scripts/storefront_schema.py"
    )
