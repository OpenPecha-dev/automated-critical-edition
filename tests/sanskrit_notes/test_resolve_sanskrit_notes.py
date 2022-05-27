from pathlib import Path
from automated_critical_edition.detect_sanskrit_notes import resolve_sanskrits
from openpecha.utils import load_yaml


def test_resolve_sanskrit_notes():
    durchen_layer = load_yaml(Path("./tests/sanskrit_notes/data/Durchen.yml/"))
    sanskrit_resolved_durchen = resolve_sanskrits(durchen_layer)
    expected_durchen_output = load_yaml(Path(f"./tests/sanskrit_notes/data/expected_durchen_output.yml"))
    assert sanskrit_resolved_durchen == expected_durchen_output