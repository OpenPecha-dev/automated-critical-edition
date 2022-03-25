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
    text_paths.sort()
    for text_path in text_paths:
        # if text_path.name in text_list:
        curr_text_notes = get_notes(text_path)











