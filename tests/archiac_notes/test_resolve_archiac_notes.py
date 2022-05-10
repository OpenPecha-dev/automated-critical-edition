from pathlib import Path
from automated_critical_edition.detect_archiac_notes import resolve_archaics
from openpecha.utils import load_yaml



def test_resolve_archiac_notes():
    base_path = "./tests/archiac_notes/data/P0001//P0001.opf/base/00001.txt"
    layers_path = "./tests/archiac_notes/data/P0001//P0001.opf/layers/"
    new_base,resolved_archiac_durchen = resolve_archaics(layers_path, base_path)
    expected_base_text = Path(f"./tests/archiac_notes/data/expected_base.txt").read_text(encoding='utf-8')
    expected_durchen_output = load_yaml(Path(f"./tests/archiac_notes/data/expected_durchen.yml"))
    assert resolved_archiac_durchen == expected_durchen_output
    assert new_base == expected_base_text
    
