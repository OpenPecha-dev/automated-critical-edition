from email.policy import default
import re
from pathlib import Path
from utils import *
from botok.third_party.has_skrt_syl import has_skrt_syl

symbol_list = [",", "།"]

def get_notes_with_span(collated_text):
    notes = []
    p = re.compile("(\(\d+\) <.+?>)")
    for m in p.finditer(collated_text):
        notes.append({"note":m.group(),"span":m.span()})
    return notes


def get_default_word(collated_text,end_index):
    index = end_index-1
    start_index = ""
    while index > 0:
        if collated_text[index] == ":":
            start_index =  index+1
            break
        elif re.search("\s",collated_text[index]):
            index_in = end_index-2
            while collated_text[index_in] != "་":
                index_in-=1
            start_index = index_in+1
            break
        index-=1
    return collated_text[start_index:end_index],start_index

def get_notes(collated_text):
    """this function gives the notes of the collated text
       as return

    Args:
        text_path (string): path to the collated_text

    Returns:
        list: list containing all the notes of the current collated text
    """
    notes_for_context = parse_notes(collated_text)
    notes_with_span = get_notes_with_span(collated_text)
    return notes_with_span, notes_for_context
        

def get_two_window(text, type):
    syls = get_syls(text)
    for num, syl in enumerate(syls,0):
        if syl in symbol_list:
            del syls[num]
    if type == "left":          
        return syls[-2]+syls[-1]
    else:
        return syls[0]+syls[1]


def get_left_and_right_context(note):
    note_csv = note[0]
    notes = re.split(r",",note_csv)
    left_context = re.sub(r"\[(.*)", "", notes[0])
    right_context = re.sub(r"(.*)\]", "", notes[-1])
    return left_context, right_context

def check_sanskrit_with_two_window(note, default_option):
    left_context, right_context = get_left_and_right_context(note)
    right_windows = get_two_window(right_context, "right")
    left_windows = get_two_window(left_context, "left")
    if right_windows and left_windows != None:
        final_text = left_windows+default_option+right_windows
        skrt = has_skrt_syl(final_text)
    return skrt


def parse_notes_for_sanskrit_words(notes_with_span, notes_for_context, collated_text):
    """it parse all the notes of the collated text
        to check if they are sanskrit words

    Args:
        list (string): list of notes
    """
    if len(notes_with_span) == len(notes_for_context):
        new_collated_text = collated_text
        for num, _ in enumerate(notes_for_context,0):
            title_check = is_title_note(notes_for_context[num])
            if title_check == False:
                start, end = notes_with_span[num]["span"]
                default_word, _ = get_default_word(collated_text,start)
                default_sanskrit_check = has_skrt_syl(default_word)
                if default_sanskrit_check:
                    new_collated_text = new_collated_text.replace(f"{notes_with_span[num]['note']}","")
                    print(f"Default is sanskrit {notes_for_context[num][0]}")
                else:
                    check = check_sanskrit_with_two_window(notes_for_context[num], default_word)
                    if check:
                        new_collated_text = new_collated_text.replace(f"{notes_with_span[num]['note']}","")
                        print(f"Majority of the windows are sanskrit {notes_for_context[num][0]}")
                    else:
                        print(f"note is not sanskrit {notes_for_context[num][0]}")
    return new_collated_text
                        
                        
                        
if __name__ == "__main__":
    paths = Path(f"./data/collated_text")
    text_paths = list(paths.iterdir())
    text_paths.sort()
    num = 0
    for text_path in text_paths:
        num += 1
        collated_text = Path(text_path).read_text(encoding='utf-8')
        print(f"\n\n{text_path.name}'s notes")
        notes_with_span, notes_for_context = get_notes(collated_text)
        new_collated_text = parse_notes_for_sanskrit_words(notes_with_span, notes_for_context, collated_text)
        Path(f"./cleaned/{text_path.name}").write_text(new_collated_text, encoding='utf-8')
        
                        











