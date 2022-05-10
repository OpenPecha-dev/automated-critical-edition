#normalize
#sort
#search
from asyncore import write
import csv
import requests
import yaml
from botok.tokenizers.wordtokenizer import WordTokenizer
from utils import *
from automated_critical_edition.detect_archiac_notes import tibetan_alp_val,normalize_word
from pathlib import Path

lekshi_gurkhang_url = 'https://raw.githubusercontent.com/Esukhia/Tibetan-archaic2modern-word/main/arch_modern.yml'


def extract_monlam_archaics(archaic_words):
    archaic_word ="བརྡ་རྙིང་།"
    with open("./dict.csv","r") as file:
        reader = csv.reader(file)
        for row in reader:
            word,desc = row     
            if desc and archaic_word in desc:
                new_word = normalize_word(word)
                if new_word != "":
                    archaic_words[new_word[0]].append(new_word)
                    
    return archaic_words

def extract_lekshi_gurkhang(archaic_words,modern_words):
    res = requests.get(lekshi_gurkhang_url)
    parsed_yaml = yaml.load(res.text, Loader=yaml.FullLoader)
    for id in parsed_yaml:
        archaic_word = normalize_word(parsed_yaml[id]['archaic'])
        if archaic_word != "":
            archaic_words[archaic_word[0]].append(archaic_word)
        modern_word = remover(parsed_yaml[id]['modern'])
        if modern_word:
            modern_words[modern_word[0][0]].extend(modern_word)
    return archaic_words,modern_words



def remover(li):
    new_li = []
    for word in li:
        new_word = normalize_word(word)
        if new_word != "":
            new_li.append(new_word)
    return new_li


def create_alph_dic():
    archaic_words = {}
    for alp in tibetan_alp_val:
        archaic_words[alp] = []

    return archaic_words    

def remove_duplicates(dic):
    for alph in dic:
        word_list = dic[alph]
        final_word_list = set(word_list)
        dic[alph] = list(final_word_list)
    return dic    

def write_yml(dic,fname):
    comb_li = []
    for key in dic:
        comb_li.extend(dic[key])
    yml_file = toyaml(comb_li)
    Path(f"./{fname}.yml").write_text(yml_file)

if __name__ == "__main__":
    archaic_words = create_alph_dic()
    modern_words = create_alph_dic()
    archaic_words  = extract_monlam_archaics(archaic_words)
    archaic_words,modern_words = extract_lekshi_gurkhang(archaic_words,modern_words)
    archaic_words = remove_duplicates(archaic_words)
    modern_words = remove_duplicates(modern_words)
    write_yml(archaic_words,"archaic_words")
    write_yml(modern_words,"modern_words")

