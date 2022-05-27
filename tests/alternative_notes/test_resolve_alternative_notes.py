from pathlib import Path
from automated_critical_edition.detect_alternative_notes import resolve_annotations
from openpecha.utils import load_yaml


def test_resolve_alternative_notes():
    durchen_layer = load_yaml(Path('./tests/alternative_notes/data/input_durchen.yml'))
    resolved_durchen = resolve_annotations(durchen_layer)
    expected_durchen_output = load_yaml(Path(f"./tests/alternative_notes/data/expected_durchen.yml"))
    assert resolved_durchen == expected_durchen_output