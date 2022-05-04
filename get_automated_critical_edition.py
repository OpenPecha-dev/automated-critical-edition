import re
from pathlib import Path
from resolve_sanskrit_notes import resolve_sanskrit_notes
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
      
  
def get_automated_critical_edition_text(opf_path):
  durchen_path = resolve_sanskrit_notes(opf_path)



if __name__ == "__main__":
  pecha_id = "PFCFAE7FE"
  opf_path = Path(f"./demo_opf/{pecha_id}/{pecha_id}.opf/")
  get_automated_critical_edition_text(opf_path)