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

def resolve_archaic_list(collated_text):
    new_collated_text=""
    char_walker = 0
    prev_end = None
    notes_with_span,notes_with_context = get_notes(collated_text)
    archaic_words = get_archaic_words()
    for note_with_span,note_with_context in zip(notes_with_span,notes_with_context):
        start,end = note_with_span["span"]
        gen_text,char_walker=build_collated_text(note_with_context,note_with_span,archaic_words,collated_text,char_walker,prev_end)
        new_collated_text+=gen_text
        prev_end = start 
    new_collated_text+=collated_text[end:]    
    return new_collated_text

def is_archaic(archaic_list,word):
    for archaic in archaic_list:
        if normalize_word(archaic) == normalize_word(word):
            return True
    return False

def is_archaic_case(archaic_list,options):
    for option in options:
        if is_archaic(archaic_list,option):
            return True

    return False

def get_modern_word(options,archaic_list):
    for option in options:
        if not is_archaic(archaic_list,option):
            return option
    return None

#istitle
#+-
#Check Archaics
#if true
#check modern

def build_collated_text(note_with_context,note_with_span,archaic_words,collated_text,char_walker,prev_end):
    gen_text = ""
    start,end = note_with_span["span"]
    default_word,default_word_start_index = get_default_word(collated_text,start,prev_end)
    alt_words = note_with_context['alt_options']
    if is_title_note(note_with_context) or len(alt_words) == 0:
        gen_text=collated_text[char_walker:end]
    elif is_archaic_case(archaic_words,alt_words):
        modern_word = get_modern_word(alt_words,archaic_words)
        gen_text=collated_text[char_walker:default_word_start_index-1]+modern_word
        modern_word= alt_words[0]
    else:
        modern_word = check_lekshi_gurkhang(alt_words)
        if modern_word != None:
            gen_text=collated_text[char_walker:default_word_start_index-1]+modern_word    
        elif modern_word == None:
            gen_text=collated_text[char_walker:end]    
    char_walker = end
    if modern_word:
        write_csv.write_csv(note_with_context,modern_word,source_file_name)
    return gen_text,char_walker

def normalize_word(word):
    puncts = ['།','་']
    for punct in puncts:
        word = word.replace(punct,"")
    return word    


def check_lekshi_gurkhang(alt_words): 
    res = requests.get(lekshi_gurkhang_url)
    parsed_yaml_file = yaml.load(res.text, Loader=yaml.FullLoader)
    result = None
    #alt_words = [remove_particles(word) for word in alt_words]
    combinations = list(itertools.product(parsed_yaml_file,alt_words))
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


def extract_archaic_words():
    archaic_words = []
    archaic_word ="བརྡ་རྙིང་།"
    with open("resources/dict.csv","r") as file:
        reader = csv.reader(file)
        for row in reader:
            word,desc = row     
            if desc and archaic_word in desc:
                archaic_words.append(word)
    return archaic_words


def get_archaic_words():
    monlam_archaics = from_yaml(Path("res/monlam_archaic_list.yml"))



def main():
    global source_file_name
    write_csv.write_csv_header()
    sources = list(Path('data/collated_text').iterdir())
    for source in sorted(sources):
        source_file_name = source.stem
        text = Path(str(source)).read_text(encoding="utf-8")
        new_text = resolve_archaic_list(text)
        print(source_file_name)
    write_csv.convert_to_excel()



if __name__ == "__main__":
    """ archaic_list = get_archaic_words()
    archaic_yml = toyaml(archaic_list)
    Path("./monlam_archaic_list.yml").write_text(archaic_yml) """
    main()

    
    

