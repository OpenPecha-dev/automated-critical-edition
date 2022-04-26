import re
from pathlib import Path
from utils import *
from resolve_sanskrit_notes import resolve_default_sanskrit_notes
from botok import WordTokenizer
from pandas import DataFrame

wt = WordTokenizer()



def check_non_word_using_botok(text, note):
    tokens = wt.tokenize(text)
    for token in tokens:
        if token.pos == 'NON_WORD':
            return True
    return False

def check_default_for_non_word(default_word, note):
    check = check_non_word_using_botok(default_word, note)
    return note, check

def check_note_options_for_non_word(default_note, note):
    num = 0
    note_options_dic = {}
    final_dic = {}
    for note_type, note_ in note['note_options'].items():
        num += 1
        if note_ != default_note:
            check = check_non_word_using_botok(note_, note)
            note_options_dic[num]={
                "note": note_,
                "note_type": note_type,
                'non_word': check
            }
            final_dic.update(note_options_dic)
            note_options_dic = {}
            
    return final_dic


def  resolve_non_word_notes(text_paths):
    
    curr_dic = {}
    final_dic = {}
    num_ = 0
    text_list = ["D3815_v056.txt","D3808_v055.txt","D3853_v057.txt", "D3889_v062.txt", 
                 "D4035_v072.txt", "D4037_v073.txt", "D4039_v074.txt",
                 "D4061_v077.txt", "D4090x_v079.txt", "D4119x_v089.txt", 
                 "D4119y_v089.txt","D4274_v108.txt","D4358x_v115.txt"]
    for text_path in text_paths:
        # text_path = Path(f"./data/collated_text/D3808_v055.txt")
        if text_path.name in text_list:
            continue
        print(text_path.name)
        collated_text = text_path.read_text(encoding='utf-8')
        sanskrit_resolved_text = resolve_default_sanskrit_notes(collated_text)
        notes = get_notes(sanskrit_resolved_text)
        for num, note in enumerate(notes,0):
            num_ += 1
            start, end = note["span"]
            _, prev_end = get_prev_note_span(notes, num)
            title_check = is_title_note(note)
            if title_check == False:
                check = check_all_notes(note)
                if check :
                    default_word, _ = get_default_word(sanskrit_resolved_text,start, prev_end)
                    note, default_non_word = check_default_for_non_word(default_word, note)
                    if default_non_word:
                        curr_dic[num_] = {
                            "left_context": note['left_context'],
                            "derge": note['note_options']['derge'],
                            "chone": note['note_options']['chone'],
                            "peking": note['note_options']['peking'],
                            "narthang": note['note_options']['narthang'],
                            "right_context": note['right_context'],
                            "non_word": default_word,
                            "source_text": text_path.name,
                        }
                        final_dic.update(curr_dic)
                        curr_dic = {}
                    else:
                        note_options_dic = check_note_options_for_non_word(default_word, note)
                        for _, info in note_options_dic.items():
                            if info['non_word']:
                                curr_dic[num_] = {
                                    "left_context": note['left_context'],
                                    "derge": note['note_options']['derge'],
                                    "peking": note['note_options']['peking'],
                                    "chone": note['note_options']['chone'],
                                    "narthang": note['note_options']['narthang'],
                                    "right_context": note['right_context'],
                                    "non_word": info['note'],
                                    "source_text": text_path.name,
                                }
                                final_dic.update(curr_dic)
                                curr_dic = {}
                        
    return final_dic

def add_to_excel(left_context, derge, chone, peking, narthang, right_context, non_word, source_text):
    df = DataFrame({'left_context':left_context, 'derge':derge, 'chone':chone, 'peking':peking, 'narthang':narthang, 'right_context':right_context, 
                    'non_word':non_word, 'source_text':source_text})
    df.to_excel('non-word-list.xlsx',sheet_name='Esukhia Work', index=True)


def create_csv(dic):
    left_context = []
    derge = []
    peking = []
    chone = []
    narthang = []
    right_context = []
    non_word = []
    source_text = []
    for _, info in dic.items():
        left_context.append(info['left_context'])
        derge.append(info['derge'])
        peking.append(info['peking'])
        chone.append(info['chone'])
        narthang.append(info['narthang'])
        right_context.append(info['right_context'])
        non_word.append(info['non_word'])
        source_text.append(info['source_text'])
    add_to_excel(left_context, derge, chone, peking, narthang, right_context, non_word, source_text)

if __name__ == "__main__":
    text_paths = list(Path(f"./data/collated_text/").iterdir())
    text_paths.sort()
    final_dic = resolve_non_word_notes(text_paths)
    create_csv(final_dic)