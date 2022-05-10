from automated_critical_edition.docx_serializer import get_base_names
from openpecha.core.pecha import OpenPechaFS

from automated_critical_edition.utils import update_durchen


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

def update_apparatus(note_options, method):
    for pub, note_info in note_options.items():
        if note_info['apparatus']:
            cur_note_apparatus = note_info['apparatus']
        else:
            cur_note_apparatus = []
        if is_punct(note_info):
            cur_note_apparatus.append(method)
            note_options[pub]['apparatus'] = cur_note_apparatus
    return note_options


def make_punctuation_note_unprintable(durchen_layer):
    for uuid, annotation in durchen_layer['annotations'].items():
        note_options = annotation['options']
        if is_punctuation_note(note_options):
            durchen_layer['annotations'][uuid]['printable'] = False
        updated_note_options = update_apparatus(note_options, method='PUNCT')
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


