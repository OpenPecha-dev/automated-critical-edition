
from openpecha.core.pecha import OpenPechaFS

from automated_critical_edition.utils import update_durchen, get_base_names, get_all_note_text, find_similarity, get_pos
from botok import BoString
from botok.vars import CharMarkers
from botok.tokenizers.wordtokenizer import WordTokenizer


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
        if note and not is_punct(note[-1]) and note[-1] != "་":
            note += '་'
        elif note:
            note = note[:-1] + '་'
        normalized_notes.append(note)
    return normalized_notes


def has_verb(notes, wt):
    for note in notes:
        tokens = wt.tokenize(note)
        for token in tokens:
            if token.pos == "VERB":
                return True
        if " བྱ་ཚིག " == get_pos(note):
            return True
    return False

def rm_empty_notes(notes):
    proper_notes = []
    for note in notes:
        if note:
            proper_notes.append(note)
    return proper_notes

def is_particle(notes, wt):
    for note in notes:
        tokens = wt.tokenize(note)
        if len(tokens) == 1 and tokens[0].pos == "PART":
            return True
    return False

def is_similar_note(note_options, wt):
    notes = get_all_note_text(note_options)
    notes = rm_empty_notes(notes)
    unique_notes = set(notes)
    if len(unique_notes) == 2:
        normalized_notes = preprocess_notes(unique_notes)
        if not has_verb(normalized_notes, wt) and not is_particle(normalized_notes, wt) and find_similarity(normalized_notes[0],normalized_notes[1]) > 0.7:
            return True
    return False

def update_features(note_options, method):
    for pub, note_info in note_options.items():
        note_options[pub]['features'] = method
    return note_options

def make_similar_note_unprintable(durchen_layer):
    wt = WordTokenizer()
    for uuid, annotation in durchen_layer['annotations'].items():
        note_options = annotation['options']
        if annotation['printable'] and is_similar_note(note_options, wt):
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