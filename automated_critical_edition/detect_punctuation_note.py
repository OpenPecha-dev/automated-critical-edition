from openpecha.core.pecha import OpenPechaFS

from automated_critical_edition.utils import update_durchen, get_base_names


def is_punct(note_info):
    puncts = ["། །", "།། །།", "།།", "༄༅༅། །", "།"]
    for punct in puncts:
        if note_info['note'] == punct:
            return True
    return False


def is_punctuation_note(note_options):
    for pub, note_info in note_options.items():
        if is_punct(note_info):
            return True
    return False

def update_features(note_options, method):
    for pub, note_info in note_options.items():
        if note_info['features']:
            cur_note_features = note_info['features']
        else:
            cur_note_features = []
        if is_punct(note_info) and method not in cur_note_features:
            cur_note_features.append(method)
            note_options[pub]['features'] = cur_note_features
    return note_options


def make_punctuation_note_unprintable(durchen_layer):
    for uuid, annotation in durchen_layer['annotations'].items():
        note_options = annotation['options']
        if is_punctuation_note(note_options):
            durchen_layer['annotations'][uuid]['printable'] = False
        updated_note_options = update_features(note_options, method='PUNCT')
        durchen_layer['annotations'][uuid]['options'] = updated_note_options
    return durchen_layer

def resolve_punctuation_notes(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        durchen_path = pecha.layers_path / base_name / "Durchen.yml"
        punctuation_resolved_durchen = make_punctuation_note_unprintable(durchen_layer)
        update_durchen(punctuation_resolved_durchen, durchen_path)


