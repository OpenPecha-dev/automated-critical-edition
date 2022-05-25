from pathlib import Path

from automated_critical_edition.utils import from_yaml
from automated_critical_edition.detect_similar_word import make_similar_note_unprintable

def test_resolve_similar_note():
    durchen_layer = from_yaml(Path('./tests/similar_notes/data/input_durchen.yml'))
    expected_durchen_layer = from_yaml(Path('./tests/similar_notes/data/expected_output.yml'))

    resolved_durchen = make_similar_note_unprintable(durchen_layer)

    assert resolved_durchen == expected_durchen_layer