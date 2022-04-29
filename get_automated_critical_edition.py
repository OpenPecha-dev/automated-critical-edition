import re
from pathlib import Path
from resolve_sanskrit_notes import resolve_sanskrit_notes
from resolve_archiac_notes import resolve_archaics
from utils import *


def get_tib_num(eng_num):
    tib_num = {
        "0": "༠",
        "1": "༡",
        "2": "༢",
        "3": "༣",
        "4": "༤",
        "5": "༥",
        "6": "༦",
        "7": "༧",
        "8": "༨",
        "9": "༩",
    }
    value = ""
    if eng_num:
        for num in str(eng_num):
            if re.search(r"\d", num):
                value += tib_num.get(num)
    return value


def update_notes_number(automated_critical_text, text_path):
  final_page = ''
  _, vol_num = get_text_id_and_vol_num(text_path)
  pages = re.split(f"({int(vol_num)}-[0-9]+)", automated_critical_text) 
  for num, page in enumerate(pages,0):
    char_walker = 0
    new_page = ''
    if num == 0 or num%2 == 0:
      notes = get_notes(page)
      for eng_num, note in enumerate(notes,1):
        tib_num = get_tib_num(eng_num)
        start, end = note['span']
        note_payload = page[start:end]
        new_note = re.sub(r"\(.*\)",fr"({tib_num})", note_payload)
        new_page += page[char_walker:start] + new_note
        char_walker = end
      if (eng_num) == len(notes) and len(notes) != 1:
            new_page += page[end:]
      elif len(notes) == 1:
          if new_page == "":
              new_page = page
          else:
            new_page += page[end:]
      final_page += new_page
    else:
      final_page += page
  return final_page
      
  
def get_automated_critical_edition_text(text_path, update_note_number=False):
  title_resolved_text = resolve_title_notes(text_path)
  line_break_removed_text = remove_line_break(title_resolved_text)
  sanskrit_note_resolved_text = resolve_sanskrit_notes(line_break_removed_text)
  archaics_note_resolved_text = resolve_archaics(sanskrit_note_resolved_text)
  automated_critical_edition_text = tranfer_line_break(text_path, archaics_note_resolved_text)
  if update_note_number:
    automated_critical_edition_text = update_notes_number(automated_critical_edition_text, text_path)
  Path(f"./cleaned/{text_path.name}").write_text(automated_critical_edition_text, encoding='utf-8')



if __name__ == "__main__":
  text_path = Path(f"./data/collated_text/D4274_v108.txt")
  get_automated_critical_edition_text(text_path)