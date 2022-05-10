from automated_critical_edition.docx_serializer import get_base_names
from openpecha.core.pecha import OpenPechaFS

from automated_critical_edition.utils import update_durchen


def is_all_note_same(note_options, default_note):
    for pub, note_info in note_options.items():
        if note_info['note'] != default_note:
            return False
    return True

def update_apparatus(note_options, method):
    for pub, note_info in note_options.items():
        if note_info['apparatus']:
            cur_note_apparatus = note_info['apparatus']
        else:
            cur_note_apparatus = []
        cur_note_apparatus.append(method)
        note_options[pub]['apparatus'] = cur_note_apparatus
    return note_options

def resolve_all_same_notes(durchen_layer):
    for uuid, annotation in durchen_layer['annotations'].items():
        default_pub = annotation['default']
        default_note = annotation['options'][default_pub]['note']
        note_options = annotation['options']
        if is_all_note_same(note_options, default_note):
            durchen_layer['annotations'][uuid]['printable'] = False
            updated_note_options = update_apparatus(note_options, method='ALL_NOTE_SAME')
            durchen_layer['annotations'][uuid]['options'] = updated_note_options
    return durchen_layer

def resolve_pedurma_mistake_note(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        durchen_path = pecha.layers_path / base_name / "Durchen.yml"
        all_same_note_resolved_durchen = resolve_all_same_notes(durchen_layer)
        update_durchen(all_same_note_resolved_durchen, durchen_path)


