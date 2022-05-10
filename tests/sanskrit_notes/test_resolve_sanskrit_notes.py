from pathlib import Path
from automated_critical_edition.resolve_sanskrit_notes import resolve_sanskrit_notes
from openpecha.utils import load_yaml



def test_resolve_sanskrit_notes():
    layers_path = "./tests/sanskrit_notes/data/layers/"
    resolved_sanskrit_durchen = resolve_sanskrit_notes(layers_path)
    expected_durchen_output = load_yaml(Path(f"./tests/sanskrit_notes/data/expected_durchen_output.yml"))
    assert resolved_sanskrit_durchen == expected_durchen_output


