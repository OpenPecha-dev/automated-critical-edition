from email.policy import default
import re
from pathlib import Path
from utils import *
from botok.third_party.has_skrt_syl import has_skrt_syl


def check_all_notes(line):
    for _, note in line['note_options'].items():
        if note == "":
            return False
    return True      

  
  
def resolve_default_sanskrit_notes(notes_with_span, notes_for_context, collated_text):
    """it parse all the notes of the collated text
        to check if they are sanskrit words

    Args:
        list (string): list of notes
    """
    char_walker = 0
    if len(notes_with_span) == len(notes_for_context):
        new_collated_text = ""
        for num, _ in enumerate(notes_for_context,0):
            if num == 1071:
                print("this is 1071")
            title_check = is_title_note(notes_for_context[num])
            start, end = notes_with_span[num]["span"]
            if title_check == False:
                check = check_all_notes(notes_for_context[num])
                if check :
                  default_word, default_start_index = get_default_word(collated_text,start)
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
            if (num+1) == len(notes_for_context) and len(notes_for_context) != 1:
                new_collated_text += collated_text[end:]
            elif len(notes_for_context) == 1:
                if new_collated_text == "":
                    new_collated_text = collated_text
                else:
                    return collated_text
    return new_collated_text
                        



if __name__ == "__main__":
    # paths = Path(f"./data/collated_text")
    # text_paths = list(paths.iterdir())
    # text_paths.sort()
    # for text_path in text_paths:
    text_path = Path(f"./data/collated_text/D4274_v108.txt")
    collated_text = Path(text_path).read_text(encoding='utf-8')
    notes_with_span, notes_for_context = get_notes(collated_text)
    new_collated_text = resolve_default_sanskrit_notes(notes_with_span, notes_for_context, collated_text)
    Path(f"./cleaned/{text_path.name}").write_text(new_collated_text, encoding='utf-8')