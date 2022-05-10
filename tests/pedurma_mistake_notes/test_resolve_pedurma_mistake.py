from pathlib import Path

from automated_critical_edition.utils import from_yaml
from automated_critical_edition.detect_pedurma_mistake import resolve_all_same_notes

def test_resolve_pedurma_mistake_note():
    durchen_layer = from_yaml(Path('./tests/pedurma_mistake_notes/data/input_durchen.yml'))
    expected_durchen_layer = from_yaml(Path('./tests/pedurma_mistake_notes/data/expected_output.yml'))

    resolved_durchen = resolve_all_same_notes(durchen_layer)

    assert resolved_durchen == expected_durchen_layer