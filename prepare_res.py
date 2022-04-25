#normalize
#sort
#search
import csv
import requests
import yaml
from botok.tokenizers.wordtokenizer import WordTokenizer
from utils import *
from pathlib import Path

lekshi_gurkhang_url = 'https://raw.githubusercontent.com/Esukhia/Tibetan-archaic2modern-word/main/arch_modern.yml'

source_file_name = ""
collated_text = ""

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
    'ས':28,
    'ཧ':29,
    'ཨ':30,
}

def extract_monlam_archaics(wt,archaic_words):
    archaic_word ="བརྡ་རྙིང་།"
    with open("./dict.csv","r") as file:
        reader = csv.reader(file)
        for row in reader:
            word,desc = row     
            if desc and archaic_word in desc:
                new_word = remove_particles(word,wt)
                if new_word != "":
                    archaic_words[new_word[0]].append(new_word)
                    
    return archaic_words

def extract_lekshi_gurkhang(wt,archaic_words,modern_words):
    res = requests.get(lekshi_gurkhang_url)
    parsed_yaml = yaml.load(res.text, Loader=yaml.FullLoader)
    for id in parsed_yaml:
        archaic_word = remove_particles(parsed_yaml[id]['archaic'],wt)
        if archaic_word != "":
            archaic_words[archaic_word[0]].append(archaic_word)
        modern_word = remover(parsed_yaml[id]['modern'],wt)
        if modern_word:
            modern_words[modern_word[0][0]].extend(modern_word)
    return archaic_words,modern_words

def remove_particles(text,wt):   
    tokenized_texts = wt.tokenize(text,split_affixes=True)
    particle_free_text = ""
    for tokenized_text in tokenized_texts:
        if tokenized_text.pos and tokenized_text.pos != "PART":
            particle_free_text+=tokenized_text.lemma
    normalized =normalize_word(particle_free_text)        
    return normalized

def remover(li,wt):
    new_li = []
    for word in li:
        new_word = remove_particles(word,wt)
        if new_word != "":
            new_li.append(new_word)
    return new_li

def normalize_word(word):
    puncts = ['།','་']
    for punct in puncts:
        word = word.replace(punct,"")
    return word 

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

if __name__ == "__main__":
    wt = WordTokenizer()
    archaic_words = create_alph_dic()
    modern_words = create_alph_dic()
    archaic_words  = extract_monlam_archaics(wt,archaic_words)
    archaic_words,modern_words = extract_lekshi_gurkhang(wt,archaic_words,modern_words)
    archaic_words = remove_duplicates(archaic_words)
    modern_words = remove_duplicates(modern_words)
    print(archaic_words)
    #dic = extract_lekshi_gurkhang(wt)
    #Path("gen_res/lekshi_gurkhang.yml").write_text(yml)


