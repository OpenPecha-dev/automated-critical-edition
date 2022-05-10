from pathlib import Path

from automated_critical_edition.utils import from_yaml
from automated_critical_edition.detect_punctuation_note import make_punctuation_note_unprintable


def test_resolve_punct_note():
    durchen_layer = from_yaml(Path('./tests/punctuation_notes/data/input_durchen.yml'))
    expected_durchen_layer = from_yaml(Path('./tests/punctuation_notes/data/expected_output.yml'))

    resolved_durchen = make_punctuation_note_unprintable(durchen_layer)

    assert resolved_durchen == expected_durchen_layer