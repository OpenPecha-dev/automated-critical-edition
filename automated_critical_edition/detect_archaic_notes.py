from pathlib import Path
from botok.tokenizers.wordtokenizer import WordTokenizer
from automated_critical_edition.utils import check_all_notes_option, get_base, update_durchen_offset, get_base_names, update_durchen, update_base
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import load_yaml

wt = WordTokenizer()

tibetan_alp_val = {
    'ཀ':1,
    'ཁ':2,
    'ག':3,
    'ང':4,
    'ཅ':5,
    'ཆ':6,
    'ཇ':7,
    'ཉ':8,
    'ཏ':9,
    'ཐ':10,
    'ད':11,
    'ན':12,
    'པ':13,
    'ཕ':14,
    'བ':15,
    'མ':16,
    'ཙ':17,
    'ཚ':18,
    'ཛ':19,
    'ཝ':20,
    'ཞ':21,
    'ཟ':22,
    'འ':23,
    'ཡ':24,
    'ར':25,
    'ལ':26,
    'ཤ':27,
    'ཥ':27,
    'ས':28,
    'ཧ':29,
    'ཨ':30,
}


def check_offset(ann_info, modern_word_pub):
    if ann_info['default'] == modern_word_pub:
        return 0
    else:
        default_pub = ann_info['default']
        default_word = ann_info['options'][default_pub]['note']
        modern_word = ann_info['options'][modern_word_pub]['note']
        offset = int(len(modern_word)- len(default_word))
        return offset


def search(target_word,words):
    low = 0
    high = len(words) - 1
    if target_word[0] not in tibetan_alp_val:
        return False
    while low <= high:
        middle = (low+high)//2
        if tibetan_alp_val[words[middle][0]] == tibetan_alp_val[target_word[0]]:
            index_plus= middle
            index_minus = middle
            while  tibetan_alp_val[words[index_minus][0]] == tibetan_alp_val[target_word[0]] or tibetan_alp_val[words[index_plus][0]] == tibetan_alp_val[target_word[0]]:
                index_plus += 1
                index_minus -= 1
                if index_plus >= len(words) or index_minus < 0:
                    break
                elif words[index_plus] == target_word or words[index_minus] == target_word:
                    return True
            return False
        elif  tibetan_alp_val[words[middle][0]] > tibetan_alp_val[target_word[0]]:
            high = middle - 1
        else:
            low =middle + 1 
    return False          


def normalize_word(word):
    if word[-1] == "།":
        word = word[:-1]
    particle_free_word = remove_particles(word)    
    return particle_free_word   


def remove_particles(text):   
    tokenized_texts = wt.tokenize(text,split_affixes=True)
    particle_free_text = ""
    for tokenized_text in tokenized_texts:
        if tokenized_text.pos and tokenized_text.pos != "PART":
            particle_free_text+=tokenized_text.text    
    return particle_free_text


def is_archaic(word, archaic_words):
    normalized_word = normalize_word(word)
    if normalized_word == "":
        return False
    elif search(normalized_word,archaic_words):
        return True
    return False

        
def get_modern_word(options, archaic_words, modern_words):
    pubs = []
    for pub, option in options.items():
        if not is_archaic(option['note'], archaic_words):
            normalize_option = normalize_word(option['note'])
            if normalize_option == "":
                return None
            if search(normalize_option, modern_words):
                return pub
            else:
                pubs.append(pub)
    if pubs:
        return pubs[0]
    else:
        return None

def is_archaic_case(options, archaic_words):
    for _, option in options.items():
        if is_archaic(option['note'], archaic_words):
            return True
    return False

def resolve_annotations(durchen):
    archaic_words,modern_words = get_archaic_modern_words()
    anns = durchen['annotations']
    for ann_id, ann_info in anns.items():
        options = ann_info['options']
        if ann_info['printable'] == True:
            all_notes = check_all_notes_option(options)
            if all_notes:
                if is_archaic_case(options, archaic_words):
                    modern_word_pub = get_modern_word(options, archaic_words, modern_words)
                    if modern_word_pub == None:
                        continue
                    elif modern_word_pub == ann_info['default']:
                        ann_info['printable']= False
                        ann_info['options'][modern_word_pub]["features"] = ["ARCHAIC"]
                    else:
                        offset = check_offset(ann_info, modern_word_pub)
                        if offset == 0:
                            continue
                        else:
                            ann_info['printable']= False
                            ann_info['default'] = modern_word_pub
                            ann_info['options'][modern_word_pub]["features"] = ["ARCHAIC"]
                            anns = update_durchen_offset(offset, anns, ann_id) 
    durchen['annotations'].update(anns)
    return durchen



def get_archaic_modern_words():
    archaic_words = load_yaml(Path("./res/archaic_words.yml"))
    modern_words = load_yaml(Path("./res/modern_words.yml"))
    return archaic_words,modern_words


def resolve_archaics(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        base_text = pecha.read_base_file(base_name)
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        durchen_path = pecha.layers_path / base_name / "Durchen.yml"
        archaic_detected_durchen = resolve_annotations(durchen_layer)
        new_base = get_base(archaic_detected_durchen, load_yaml(durchen_path), base_text, "ARCHAIC")
        update_durchen(archaic_detected_durchen, durchen_path)
        update_base(opf_path, base_name, new_base)