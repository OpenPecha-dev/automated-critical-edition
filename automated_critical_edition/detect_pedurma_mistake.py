from openpecha.core.pecha import OpenPechaFS

from automated_critical_edition.utils import update_durchen, get_base_names


def is_all_note_same(note_options, default_note):
    for pub, note_info in note_options.items():
        if note_info['note'] != default_note:
            return False
    return True

def update_features(note_options, method):
    for pub, note_info in note_options.items():
        if note_info['features']:
            cur_note_features = note_info['features']
        else:
            cur_note_features = []
        if method not in cur_note_features:
            cur_note_features.append(method)
            note_options[pub]['features'] = cur_note_features
    return note_options

def resolve_all_same_notes(durchen_layer):
    for uuid, annotation in durchen_layer['annotations'].items():
        default_pub = annotation['default']
        default_note = annotation['options'][default_pub]['note']
        note_options = annotation['options']
        if annotation['printable'] and is_all_note_same(note_options, default_note):
            durchen_layer['annotations'][uuid]['printable'] = False
            updated_note_options = update_features(note_options, method='ALL_NOTE_SAME')
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


