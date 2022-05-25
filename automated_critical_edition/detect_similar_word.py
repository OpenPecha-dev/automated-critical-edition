from openpecha.core.pecha import OpenPechaFS

from automated_critical_edition.utils import update_durchen, get_base_names, get_all_note_text
from botok import BoString
from botok.vars import CharMarkers
import requests


def is_punct(string):
    normal_punt = CharMarkers(5)
    special_punt = CharMarkers(6)
    bo_string = BoString(string)
    for _, char_marker_value in bo_string.base_structure.items():
        char_maker = CharMarkers(char_marker_value)
        if char_maker == normal_punt or char_maker == special_punt:
            return True
    return False

def preprocess_notes(notes):
    normalized_notes = []
    for note in notes:
        if not is_punct(note[-1]):
            note += '་'
        else:
            note[-1] = '་'
        normalized_notes.append(note)
    return normalized_notes

def get_similarity(normalized_notes):
    r = requests.post(url='https://hf.space/embed/openpecha/word_vectors_classical_bo/+/api/predict/', json={"data": [normalized_notes[0],normalized_notes[1]]})
    similarity_info = r.json()
    return similarity_info

def is_similar_note(note_options):
    notes = get_all_note_text(note_options)
    unique_notes = set(notes)
    if len(unique_notes) == 2:
        normalized_notes = preprocess_notes(unique_notes)
        if has_verb_notes(normalized_notes) and get_similarity(normalized_notes) > 0.7:
            return True
    return False

def update_features(note_options, method):
    for pub, note_info in note_options.items():
        note_options[pub]['features'] = method
    return note_options

def make_similar_note_unprintable(durchen_layer):
    for uuid, annotation in durchen_layer['annotations'].items():
        note_options = annotation['options']
        if annotation['printable'] and is_similar_note(note_options):
            durchen_layer['annotations'][uuid]['printable'] = False
        updated_note_options = update_features(note_options, method='SIMILAR')
        durchen_layer['annotations'][uuid]['options'] = updated_note_options
    return durchen_layer

def resolve_similar_notes(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        durchen_path = pecha.layers_path / base_name / "Durchen.yml"
        similar_note_resolved_durchen = make_similar_note_unprintable(durchen_layer)
        update_durchen(similar_note_resolved_durchen, durchen_path)