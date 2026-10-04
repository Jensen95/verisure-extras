# ABOUTME: Tests that translations/en.json matches strings.json and covers errors raised.
# ABOUTME: Guards against drift since custom integrations only ship translations/en.json.
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent / "custom_components" / "verisure_extras"


def test_en_translations_match_strings() -> None:
    """translations/en.json is a copy of strings.json."""
    strings = json.loads((ROOT / "strings.json").read_text(encoding="utf-8"))
    en = json.loads((ROOT / "translations" / "en.json").read_text(encoding="utf-8"))
    assert strings == en


def test_translations_cover_flow_and_exceptions() -> None:
    """Every error key the code can raise has a translation."""
    en = json.loads((ROOT / "translations" / "en.json").read_text(encoding="utf-8"))
    assert "invalid_pin" in en["config"]["error"]
    assert "invalid_pin" in en["options"]["error"]
    assert {"code_required", "source_call_failed"} <= set(en["exceptions"])
    assert "{entity_id}" in en["exceptions"]["source_call_failed"]["message"]
