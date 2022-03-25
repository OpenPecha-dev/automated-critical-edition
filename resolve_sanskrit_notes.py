import re
from pathlib import Path
from utils import *



def get_notes(text_path):
    """this function gives the notes of the collated text
       as return

    Args:
        text_path (string): path to the collated_text

    Returns:
        list: list containing all the notes of the current collated text
    """
    collated_text = Path(text_path).read_text(encoding='utf-8')
    cur_text_notes = parse_notes(collated_text)
    return cur_text_notes

# def check_for_sanskrit()


if __name__ == "__main__":
    paths = Path(f"./data/collated_text")
    text_paths = list(paths.iterdir())
    text_list = ["D1494_v011.txt"]
    text_paths.sort()
    for text_path in text_paths:
        # if text_path.name in text_list:
        curr_text_notes = get_notes(text_path)
        num = 0
        for note in curr_text_notes:
            check = is_title_note(note)
            if check:
                num += 1
                if num >= 2:
                    print(f"{text_path.name} 2")
                    break
            #     break
            # else:
            #     print(f"{text_path.name} 0")
            #     break
            
                # sanskrit_check = check_default_for_sanskrit(default_option)
                
            # get_notes_samples(collated_text, note_samples=)











