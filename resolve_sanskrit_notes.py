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
        title_check = is_title_note(note)
        if title_check == False:
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
