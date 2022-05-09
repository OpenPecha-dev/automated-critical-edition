from automated_critical_edition.docx_serializer import get_base_names
from openpecha.core.pecha import OpenPechaFS

from automated_critical_edition.utils import update_durchen


def is_outlier_note(note_options):
    notes = list(note_options.values())
    for note in notes:
        if notes.count(note) == 3:
            return True
    return False


def make_outlier_note_unprintable(durchen_layer):
    for uuid, annotation in durchen_layer['annotations'].items():
        note_options = annotation['options']
        if is_outlier_note(note_options):
            durchen_layer['annotations'][uuid]['printable'] = False
    return durchen_layer

def resolve_outlier_notes(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        durchen_path = pecha.layers_path / base_name / "Durchen.yml"
        outlier_note_resolved_durchen = make_outlier_note_unprintable(durchen_layer)
        update_durchen(outlier_note_resolved_durchen, durchen_path)