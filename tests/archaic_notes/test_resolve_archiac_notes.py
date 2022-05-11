from pathlib import Path
from automated_critical_edition.detect_archaic_notes import resolve_archaics
from openpecha.utils import load_yaml



def test_resolve_archaic_notes():
    base_path = "./tests/archaic_notes/data/P0001//P0001.opf/base/00001.txt"
    layers_path = "./tests/archaic_notes/data/P0001//P0001.opf/layers/"
    new_base,resolved_archaic_durchen = resolve_archaics(layers_path, base_path)
    expected_base_text = Path(f"./tests/archaic_notes/data/expected_base.txt").read_text(encoding='utf-8')
    expected_durchen_output = load_yaml(Path(f"./tests/archaic_notes/data/expected_durchen.yml"))
    assert resolved_archaic_durchen == expected_durchen_output
    assert new_base == expected_base_text
    