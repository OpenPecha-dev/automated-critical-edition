from automated_critical_edition.docx_serializer import get_base_names
from openpecha.core.pecha import OpenPechaFS

from automated_critical_edition.utils import update_durchen

def get_all_note_text(note_options):
    note_texts = []
    for pub, note_info in note_options.items():
        note_texts.append(note_info['note'])
    return note_texts

def is_outlier_note(note_options):
    notes = get_all_note_text(note_options)
    for note in notes:
        if notes.count(note) == 3:
            return True
    return False

def update_apparatus(note_options, method):
    outlier_note = ''
    notes = get_all_note_text(note_options)
    for note in notes:
        if notes.count(note) == 1:
            outlier_note = note
    if outlier_note:
        for pub, note_info in note_options.items():
            if note_info['apparatus']:
                cur_note_apparatus = note_info['apparatus']
            else:
                cur_note_apparatus = []
            if note_info['note'] == outlier_note:
                cur_note_apparatus.append(method)
                note_options[pub]['apparatus'] = cur_note_apparatus
    return note_options

def make_outlier_note_unprintable(durchen_layer):
    for uuid, annotation in durchen_layer['annotations'].items():
        note_options = annotation['options']
        if is_outlier_note(note_options):
            durchen_layer['annotations'][uuid]['printable'] = False
        updated_note_options = update_apparatus(note_options, method='OUTLIER')
        durchen_layer['annotations'][uuid]['options'] = updated_note_options
    return durchen_layer

def resolve_outlier_notes(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        durchen_path = pecha.layers_path / base_name / "Durchen.yml"
        outlier_note_resolved_durchen = make_outlier_note_unprintable(durchen_layer)
        update_durchen(outlier_note_resolved_durchen, durchen_path)