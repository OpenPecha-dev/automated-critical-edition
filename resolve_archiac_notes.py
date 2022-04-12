import re
from sqlite3 import Row
from unittest import result
import utils
import itertools
import yaml
import csv
import requests
from pathlib import Path
from botok.tokenizers.wordtokenizer import WordTokenizer
from utils import get_notes_with_span,parse_notes,is_title_note


lekshi_gurkhang_url = 'https://raw.githubusercontent.com/Esukhia/Tibetan-archaic2modern-word/main/arch_modern.yml'


def resolve_archaics(collated_text):
    new_collated_text=""
    char_walker = 0
    notes_with_span = get_notes_with_span(collated_text)
    notes_with_context = parse_notes(collated_text)
    archaic_words = get_archaic_words()
    for note_with_span,note_with_context in zip(notes_with_span,notes_with_context):
        _,end = note_with_span["span"]
        gen_text,char_walker=build_collated_text(note_with_context,note_with_span,archaic_words,collated_text,char_walker)
        new_collated_text+=gen_text
    new_collated_text+=collated_text[end:]    
    return new_collated_text


def build_collated_text(note_with_context,note_with_span,archaic_words,collated_text,char_walker):
    gen_text = ""
    foot_note = note_with_span["note"]
    start,end = note_with_span["span"]
    default_word,default_word_start_index = get_default_word(collated_text,start)
    alt_words = get_alternative_words(note_with_context[1])
    modern_word = check_lekshi_gurkhang(alt_words)
    write_csvs = True
    if is_title_note(note_with_context) or len(alt_words) == 0:
        gen_text=collated_text[char_walker:end]
        write_csvs = False 
    elif default_word in archaic_words:
        gen_text=collated_text[char_walker:default_word_start_index-1]+alt_words[0]
        modern_word= alt_words[0]
    elif modern_word != None:
        gen_text=collated_text[char_walker:default_word_start_index-1]+modern_word    
    elif modern_word == None:
        gen_text=collated_text[char_walker:end]    
    char_walker = end+1
    if write_csvs:
        write_csv(note_with_context,modern_word)
    return gen_text,char_walker


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
    """ regex = "»([^(«|>)]*)"
    texts = re.findall(regex,note) """
    texts = list(note.values())
    for text in texts:
        if text == "" or "-" in text or "+" in text:
            continue
        words.append(text.replace("\n",""))
    return words


def check_lekshi_gurkhang(alt_words): 
    res = requests.get(lekshi_gurkhang_url)
    parsed_yaml_file = yaml.load(res.text, Loader=yaml.FullLoader)
    result = None
    alt_words = [remove_particles(word) for word in alt_words]
    combinations = list(itertools.product(parsed_yaml_file,alt_words))
    for combination in combinations:
        id,word = combination
        modern_words = parsed_yaml_file[id]['modern']
        if word in modern_words:
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

def write_csv(note_with_context,modern_word):
    with open("feed.csv","a") as file:
        writer = csv.writer(file)
        row = get_alternative_words(note_with_context[1])
        if modern_word == None:
            modern_word = "None"
        row.append(modern_word)
        print(row)
        writer.writerow(row)


if __name__ == "__main__":
    text = Path("data/collated_text/D1115_v001.txt").read_text(encoding="utf-8")
    new_text = resolve_archaics(text)

