from cgitb import text
from email.policy import default
from pathlib import Path
from tracemalloc import start
from resolve_sanskrit_notes import get_prev_note_span
from utils import *
from pandas import DataFrame



def get_average_payload_syl_count(notes, default_note):
    syl_len = 0
    total_note = 0
    for _, note_option in notes['note_options'].items():
        if note_option != "":
            if "……" in note_option:
                return None
            elif note_option == default_note:
                pass
            else:
                syls = get_syls(note_option)
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


def get_page_num(collated_text, colon_pos, start, vol_num):
    pages = re.split(f"({int(vol_num)}-[0-9]+)", collated_text)
    for page_num, page in enumerate(pages,0):
        if page_num == 0 or page_num%2 == 0:
            note = collated_text[colon_pos-10:start+10]
            if note in page:
                return re.split(r"\-", pages[page_num+1])[1]
            else:
                note = collated_text[colon_pos-10:colon_pos]
                if note in page:
                    return re.split(r"\-", pages[page_num+1])[1]
            
            
def check_syl_count(avg_payload_syl_count, syl_count):
    if avg_payload_syl_count :
        if abs(avg_payload_syl_count-syl_count) <= 2:
            return False
        else:
            return True
    else:
        return False

def check_shad_near_colon(collated_text, colon_pos):
    if colon_pos:
        text_near_colon = collated_text[colon_pos-3:colon_pos]
        if "།" in text_near_colon:
            return True
        
    return False

def check_page_num(page_num, text_id_and_pages, text_path):
    if page_num:
        for info in text_id_and_pages:
            text_id = re.split(r",", info)[0]
            if text_id == text_path.name:
                page = re.split(r",", info)[1]
                if page == page_num:
                    return False
    return True 
    
def review_collated_text(text_paths):
    s_no = 0
    final_dic = {}
    text_id_and_page = Path(f"./text_with_page.txt").read_text(encoding='utf-8').splitlines()
    for text_path in text_paths:
        if text_path.name in text_id_and_page:
            continue
        curr_text = {}
        page_nums = []
        print(text_path.name)
        text_id, vol_num = get_text_id_and_vol_num(text_path)
        collated_text = text_path.read_text(encoding='utf-8')
        
        notes = get_notes(collated_text)
        for num, note in enumerate(notes,0):
            start, _ = note["span"]
            _, prev_end = get_prev_note_span(notes, num)
            colon_pos = get_colon_pos(collated_text, start, prev_end)
            shad_check = check_shad_near_colon(collated_text, colon_pos)
            if shad_check == False:
                default_note = note['default_option']
                if colon_pos:
                    syl_count = len(get_syls(collated_text[colon_pos:start]))
                    if syl_count:
                        avg_payload_syl_count = get_average_payload_syl_count(note, default_note)
                        check = check_syl_count(avg_payload_syl_count, syl_count)
                        if check:
                            page_num = get_page_num(collated_text, colon_pos, start, vol_num)
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
            else:
                page_num = get_page_num(collated_text, colon_pos, start, vol_num)
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
    return final_dic

def add_to_excel(source_texts,page_nums,links, all_status):
    df = DataFrame({'Source Text': source_texts,'Page Number':page_nums,'Link':links,'Status':all_status})
    df.to_excel('Collated_text_review_needed.xlsx',sheet_name='Esukhia Work', index=True)


def get_number_of_notes(text_id):
    list = (Path(f"./batch4_with_note_num.txt").read_text(encoding='utf-8')).splitlines()
    for pecha in list:
        infos = pecha.split(",")
        pecha_id = infos[0]
        if pecha_id == text_id:
            note_num = int(infos[1])
            return note_num

def create_csv(dic):
    source_texts = []
    page_nums = []
    links = []
    all_status = []
    status = "Not Done"
    for _, info in dic.items():
        source_texts.append(info['source_text'])
        page_nums.append(info['page_num'])
        links.append(info['link'])
        all_status.append(status)
    add_to_excel(source_texts, page_nums, links, all_status)

if __name__ == "__main__":
    text_paths = list(Path(f"./data/collated_text/").iterdir())
    text_paths.sort()
    final_dic = review_collated_text(text_paths)
    create_csv(final_dic)