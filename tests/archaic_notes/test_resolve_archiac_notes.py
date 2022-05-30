from pathlib import Path
import re
from automated_critical_edition.detect_archaic_notes import resolve_durchen_notes
from automated_critical_edition.utils import get_base
from openpecha.utils import load_yaml, dump_yaml



def test_resolve_archaic_notes():
    durchen_layer = load_yaml(Path('./tests/archaic_notes/data/input_durchen.yml'))
    base_text = Path('./tests/archaic_notes/data/input_base.txt').read_text(encoding='utf-8')
    resolved_archaic_durchen = resolve_durchen_notes(durchen_layer)
    new_base = get_base(resolved_archaic_durchen, load_yaml(Path('./tests/archaic_notes/data/input_durchen.yml')), base_text, "ARCHAIC" )
    expected_base_text = Path(f"./tests/archaic_notes/data/expected_base.txt").read_text(encoding='utf-8')
    expected_durchen_output = load_yaml(Path(f"./tests/archaic_notes/data/expected_durchen.yml"))
    assert resolved_archaic_durchen == expected_durchen_output
    assert new_base == expected_base_text

if __name__ == "__main__":
    test_resolve_archaic_notes()