from logging import NOTSET
import re
import itertools
from tracemalloc import start
from numpy import source
from pyparsing import Word
import yaml
import csv
import requests
from pathlib import Path
from botok.tokenizers.wordtokenizer import WordTokenizer
from utils import *
import write_csv

lekshi_gurkhang_url = 'https://raw.githubusercontent.com/Esukhia/Tibetan-archaic2modern-word/main/arch_modern.yml'
source_file_name = ""
collated_text = ""
archaic_words = []
modern_words = []

def built_text():
    new_collated_text=""
    char_walker = 0
    end = ""
    notes = get_notes(collated_text)
    for note in notes:
        _,end = note["span"]
        gen_text,char_walker=reform_text(note,char_walker)
        new_collated_text+=gen_text
    new_collated_text+=collated_text[end:]    
    return new_collated_text


def reform_text(note,char_walker):
    gen_text = ""
    modern_word = None
    _,end = note["span"]
    default_word_start_index = get_default_word_start(collated_text,note)
    alt_options = note['alt_options']
    if is_title_note(note) or len(alt_options) == 0:
        gen_text=collated_text[char_walker:end]
    elif is_archaic_case(alt_options):
        modern_word = get_modern_word(alt_options)
        if modern_word != None:
            gen_text=collated_text[char_walker:default_word_start_index]+modern_word
        else:
            gen_text=collated_text[char_walker:end] 
    else:
        gen_text=collated_text[char_walker:end]    
    char_walker = end
    if modern_word:
        write_csv.write_csv(note,modern_word,source_file_name)
    return gen_text,char_walker

 


def normalize_word(word):
    puncts = ['།','་']
    for punct in puncts:
        word = word.replace(punct,"")
    return word    


def check_lekshi_gurkhang(alt_options): 
    res = requests.get(lekshi_gurkhang_url)
    parsed_yaml_file = yaml.load(res.text, Loader=yaml.FullLoader)
    result = None
    #alt_options = [remove_particles(word) for word in alt_options]
    combinations = list(itertools.product(parsed_yaml_file,alt_options))
    for id,word in combinations.items():
        modern_words = parsed_yaml_file[id]['modern']
        for modern_word in modern_words:
            if normalize_word(word) == normalize_word(modern_word):
                result = word
                break
    return result       


def remove_particles(text):   
    wt = WordTokenizer()
    tokenized_texts = wt.tokenize(text,split_affixes=True)
    particle_free_text = ""
    for tokenized_text in tokenized_texts:
        if tokenized_text.pos and tokenized_text.pos != "PART":
            particle_free_text+=tokenized_text.text    
    return particle_free_text


def get_archaic_modern_words():
    global archaic_words,modern_words
    monlam_archaics = from_yaml(Path("./res/monlam_archaics.yml"))
    lg_archaics,lg_moderns = extract_lekshi_gurkhang()
    archaic_words.extend(monlam_archaics)
    archaic_words.extend(lg_archaics)
    modern_words.extend(lg_moderns)


def is_archaic(word):
    for archaic in archaic_words:
        if normalize_word(archaic) == normalize_word(word):
            return True
    return False

def is_archaic_case(options):
    for option in options:
        if is_archaic(option):
            return True

    return False

def get_modern_word(options):
    for option in options:
        if not is_archaic(option):
            if option in modern_words:
                return option
    return None

def extract_lekshi_gurkhang():
    res = requests.get(lekshi_gurkhang_url)
    parsed_yaml = yaml.load(res.text, Loader=yaml.FullLoader)
    archaics = []
    modern = []
    for id in parsed_yaml:
        archaics.append(parsed_yaml[id]['archaic'])
        modern.extend(parsed_yaml[id]['modern'])
    return archaics,modern

def extract_monlam_archaics():
    archaic_words = []
    archaic_word ="བརྡ་རྙིང་།"
    with open("resources/dict.csv","r") as file:
        reader = csv.reader(file)
        for row in reader:
            word,desc = row     
            if desc and archaic_word in desc:
                archaic_words.append(word)
    return archaic_words


def resolve_archaics(text):
    global collated_text
    collated_text = text
    get_archaic_modern_words()
    new_text = built_text()
    return new_text


def main():
    global source_file_name
    sources = list(Path('data/collated_text').iterdir())
    for source in sorted(sources):
        source_file_name = source.stem
        collated_text = Path(str(source)).read_text(encoding="utf-8")
        resolve_archaics(collated_text)
    write_csv.convert_to_excel()


if __name__ == "__main__":
    text = Path("./data/collated_text/D1115_v001.txt").read_text(encoding="utf-8")
    new_text = resolve_archaics(text)
    Path("./gen.txt").write_text(new_text)

    
    

