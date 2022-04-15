from email.policy import default
from pathlib import Path
from tracemalloc import start
from resolve_sanskrit_notes import get_prev_note_span
from utils import *



def get_average_payload_syl_count(notes, default_note):
    syl_len = 0
    total_note = 0
    for _, note in notes['note_options'].items():
        if note != "":
            if "……" in note:
                return None
            elif note == default_note:
                pass
            else:
                syls = get_syls(note)
                syl_len += len(syls)
                total_note += 1
    if total_note != 0:
        average_payload_syl = syl_len/total_note
        return average_payload_syl
    else:
        return None


def get_colon_pos(collated_text, end_index, prev_end):
    if prev_end == None:
        prev_end = 0
    if ":" in collated_text[prev_end:end_index]:
        span = collated_text[prev_end:end_index].find(":")
        colon_pos = span + prev_end + 1
        return colon_pos
    else:
        return None

def get_text_id_and_vol_num(text_path):
    text_name = text_path.name[:-4]
    map = re.match(r"([A-Z][0-9]+[a-z]?)\_(v[0-9]+)",text_name)
    text_id = map.group(1)
    vol_num = map.group(2)[1:]
    return text_id, vol_num



def get_page_num(collated_text, note, vol_num):
    pages = re.split(f"({int(vol_num)}-[0-9]+)", collated_text)
    for page_num, page in enumerate(pages,0):
        if page_num == 0 or page_num%2 == 0:
            if note in page:
                return re.split(r"\-", pages[page_num+1])[1]

def review_collated_text(text_paths):
    for text_path in text_paths:
        s_no = 0
        curr_text = {}
        final_dic = {}
        page_nums = []
        text_id, vol_num = get_text_id_and_vol_num(text_path)
        collated_text = text_path.read_text(encoding='utf-8')
        
        notes_with_span, notes_for_context = get_notes(collated_text)
        if len(notes_with_span) == len(notes_for_context) :
            for note_num, _ in enumerate(notes_for_context, 0):
                start_pos, _ = notes_with_span[note_num]['span']
                _, prev_end = get_prev_note_span(notes_with_span, note_num)
                colon_pos = get_colon_pos(collated_text, start_pos, prev_end)
                default_note = notes_for_context[note_num]['default_option']
                if colon_pos:
                    syl_count = len(get_syls(collated_text[colon_pos:start_pos]))
                    if syl_count:
                        avg_payload_syl_count = get_average_payload_syl_count(notes_for_context[note_num], default_note)
                        if avg_payload_syl_count :
                            if avg_payload_syl_count != syl_count:
                                page_num = get_page_num(collated_text, collated_text[colon_pos-10:start_pos+10], vol_num)
                                if page_num not in page_nums:
                                    s_no += 1
                                    curr_text[s_no] = {
                                        "source_text": text_path.name,
                                        "page_num": page_num,
                                        "link": f"https://openpecha.bdrc.io/pedurma/{text_id}"
                                    }
                                    final_dic.update(curr_text)
                                    curr_text = {}
                                    page_nums.append(page_num)
                                continue
    return final_dic



if __name__ == "__main__":
    text_paths = list(Path(f"./data/collated_text/").iterdir())
    text_paths.sort()
    # text_paths = [Path(f"./data/collated_text/D4274_v108.txt")]
    final_dic = review_collated_text(text_paths)
    print(final_dic)