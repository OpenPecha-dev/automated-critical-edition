import re
from pathlib import Path
from utils import *
from resolve_sanskrit_notes import resolve_default_sanskrit_notes
from botok import WordTokenizer

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
        if note_ != default_note:
            num += 1
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
    text_list = ["D1765_v014.txt","D1778_v014.txt", "D1784_v015.txt"]
    for text_path in text_paths:
        # text_path = Path(f"./data/collated_text/D1784_v015.txt")
        if text_path.name in text_list:
            continue
        collated_text = text_path.read_text(encoding='utf-8')
        sanskrit_resolved_text = resolve_default_sanskrit_notes(collated_text)
        notes = get_notes(sanskrit_resolved_text)
        for num, note in enumerate(notes,0):
            start, end = note["span"]
            _, prev_end = get_prev_note_span(notes, num)
            title_check = is_title_note(note)
            if title_check == False:
                check = check_all_notes(note)
                if check :
                    default_word, _ = get_default_word(sanskrit_resolved_text,start, prev_end)
                    note, default_non_word = check_default_for_non_word(default_word, note)
                    if default_non_word:
                        curr_dic[num] = {
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
                                curr_dic[num] = {
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
        print(text_path.name)
                        
    return final_dic

if __name__ == "__main__":
    text_paths = list(Path(f"./data/collated_text/").iterdir())
    text_paths.sort()
    final_dic = resolve_non_word_notes(text_paths)