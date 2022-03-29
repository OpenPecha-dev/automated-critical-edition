import re
from unittest import result
import utils
import itertools
import yaml
import csv
import requests
from pathlib import Path
from botok.tokenizers.wordtokenizer import WordTokenizer

arch_modern_url = 'https://raw.githubusercontent.com/Esukhia/Tibetan-archaic2modern-word/main/arch_modern.yml'

def resolve_archaics(collated_text):
    new_collated_text=""
    char_walker = 0
    notes = get_notes(collated_text)
    archaic_words = get_archaic_words()
    for note in notes:
        foot_note = note["note"]
        start,end = note["span"]
        default_word,default_word_start_index = get_default_word(collated_text,start)
        alt_words = get_alternative_words(foot_note)
        modern_word = check_lekshi_gurkhang(alt_words)
        if default_word in archaic_words:
            new_collated_text+=collated_text[char_walker:default_word_start_index-1]+alt_words[0]
        elif modern_word != None:
            new_collated_text+=collated_text[char_walker:default_word_start_index-1]+modern_word    
        elif modern_word == None:
            new_collated_text+=collated_text[char_walker:end]    
        char_walker = end+1
    return new_collated_text


def get_notes(collated_text):
    notes = []
    p = re.compile("\d+\s*<[^>]*>")
    for m in p.finditer(collated_text):
        notes.append({"note":m.group(),"span":m.span()})
    return notes


def get_default_word(collated_text,end_index):
    index = end_index-1
    start_index = ""
    while index > 0:
        if collated_text[index] == ":":
            start_index =  index+1
            break
        elif re.search("\s",collated_text[index]):
            index_in = end_index-2
            while collated_text[index_in] != "་":
                index_in-=1
            start_index = index_in+1
            break
        index-=1
    return collated_text[start_index:end_index],start_index


def get_alternative_words(note):
    words =[]
    regex = "»([^(«|>)]*)"
    texts = re.findall(regex,note)
    for text in texts:
        if text == "":
            continue
        words.append(text)
    return words


def check_lekshi_gurkhang(alt_words): 
    res = requests.get(arch_modern_url)
    parsed_yaml_file = yaml.load(res.text, Loader=yaml.FullLoader)
    result = None
    combinations = list(itertools.product(parsed_yaml_file,alt_words))
    for combination in combinations:
        id,word = combination
        particle_free_word = remove_particles(word)
        modern_words = parsed_yaml_file[id]['modern']
        if particle_free_word in modern_words:
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


def get_archaic_words():
    archaic_words = []
    archaic_word ="བརྡ་རྙིང་།"
    with open("resources/dict.csv","r") as file:
        reader = csv.reader(file)
        for row in reader:
            word,desc = row     
            if desc and archaic_word in desc:
                archaic_words.append(word)
    return archaic_words


