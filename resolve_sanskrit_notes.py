from pathlib import Path
from utils import *
from botok.third_party.has_skrt_syl import has_skrt_syl
    
  
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
        start, end = note["span"]
        _, prev_end = get_prev_note_span(notes, num)
        check = check_all_notes(note)
        if check :
            default_word, default_start_index = get_default_word(collated_text,start, prev_end)
            default_sanskrit_check = has_skrt_syl(default_word)
            if default_sanskrit_check:
                if collated_text[default_start_index-1:default_start_index] == ":":
                    new_collated_text += collated_text[char_walker:default_start_index-1] + default_word
                else:
                    new_collated_text += collated_text[char_walker:default_start_index] + default_word
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


def get_replacement_note(notes):
    replacement_note = []
    for _, note in notes['note_options'].items():
        if has_skrt_syl(note):
            replacement_note.append(note)
    if len(replacement_note) == 1:
        return replacement_note[0]
    elif len(replacement_note) == 2:
        if replacement_note[0] == replacement_note[1]:
            return replacement_note[0]
    elif len(replacement_note) == 3:
        if replacement_note[0] == replacement_note[1] == replacement_note[2]:
            return replacement_note[0]
    else:
        return None
    

def resolve_sanskrit_optional_notes(collated_text):
    char_walker = 0
    new_collated_text = ""
    notes = get_notes(collated_text)
    for num, note in enumerate(notes,0):
        start, end = note["span"]
        _, prev_end = get_prev_note_span(notes, num)
        check = check_all_notes(note)
        if check :
            default_word, default_start_index = get_default_word(collated_text,start, prev_end)
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