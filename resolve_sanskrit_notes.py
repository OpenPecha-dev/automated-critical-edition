from pathlib import Path
from utils import *
from botok.third_party.has_skrt_syl import has_skrt_syl
from botok import WordTokenizer

wt = WordTokenizer()
  
def resolve_default_sanskrit_notes(collated_text):
    """it parse all the notes of the collated text
        to check if they are sanskrit words

    Args:
        list (string): list of notes
    """
    char_walker = 0
    new_collated_text = ""
    notes = get_notes(collated_text)
    for num, note in enumerate(notes,0):
        _, end = note["span"]
        check = check_all_notes(note)
        if check :
            default_option = note['default_option']
            default_start_index, _ = note['default_option_span']
            default_sanskrit_check = has_skrt_syl(default_option)
            if default_sanskrit_check:
                if collated_text[default_start_index-1:default_start_index] == ":":
                    new_collated_text += collated_text[char_walker:default_start_index-1] + default_option
                else:
                    new_collated_text += collated_text[char_walker:default_start_index] + default_option
                char_walker = end
            elif check_for_sanskrit_syl(default_option):
                if collated_text[default_start_index-1:default_start_index] == ":":
                    new_collated_text += collated_text[char_walker:default_start_index-1] + default_option
                else:
                    new_collated_text += collated_text[char_walker:default_start_index] + default_option
                char_walker = end
            else:
                new_collated_text += collated_text[char_walker:end]
                char_walker = end
        if (num+1) == len(notes) and len(notes) != 1:
            new_collated_text += collated_text[end:]
        elif len(notes) == 1:
            if new_collated_text == "":
                new_collated_text = collated_text
            else:
                new_collated_text += collated_text[end:]
    return new_collated_text

def check_for_sanskrit_syl(note):
    tokens = wt.tokenize(note)
    for token in tokens:
        if token.skrt:
            return True
    return False

def get_replacement_note(note):
    replacement_notes = []
    for _, note_option in note['note_options'].items():
        if has_skrt_syl(note_option):
            replacement_notes.append(note_option)
        elif check_for_sanskrit_syl(note_option):
            replacement_notes.append(note_option)
    if len(replacement_notes) == 1:
        replacement_note = replacement_notes[0]
    elif len(replacement_notes) == 2:
        if replacement_notes[0] == replacement_notes[1]:
            replacement_note = replacement_notes[0]
    elif len(replacement_notes) == 3:
        if replacement_notes[0] == replacement_notes[1] == replacement_notes[2]:
            replacement_note = replacement_notes[0]
    else:
        replacement_note = None
    
    corrected_note = correct_shad_and_tsek_in_note(note['default_option'], replacement_note)
    return corrected_note

def resolve_sanskrit_optional_notes(collated_text):
    char_walker = 0
    new_collated_text = ""
    notes = get_notes(collated_text)
    for num, note in enumerate(notes,0):
        _, end = note["span"]
        check = check_all_notes(note)
        if check :
            default_start_index, _ = note['default_option_span']
            sanskrit_note_option = get_replacement_note(note)
            if sanskrit_note_option:
                if collated_text[default_start_index-1:default_start_index] == ":":
                    new_collated_text += collated_text[char_walker:default_start_index-1] + sanskrit_note_option
                else:
                    new_collated_text += collated_text[char_walker:default_start_index] + sanskrit_note_option
                char_walker = end
            else:
                new_collated_text += collated_text[char_walker:end]
                char_walker = end
        if (num+1) == len(notes) and len(notes) != 1:
            new_collated_text += collated_text[end:]
        elif len(notes) == 1:
            if new_collated_text == "":
                new_collated_text = collated_text
            else:
                new_collated_text += collated_text[end:]
    return new_collated_text



def resolve_sanskrit_notes(collated_text):
    default_resolved_text = resolve_default_sanskrit_notes(collated_text)
    final_text = resolve_sanskrit_optional_notes(default_resolved_text)
    return final_text