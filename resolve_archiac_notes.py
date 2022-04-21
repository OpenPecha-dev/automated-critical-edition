from locale import normalize
from logging import NOTSET
import re
import itertools
from tracemalloc import start
from numpy import source
from pyparsing import Word
import yaml
from pathlib import Path
from botok.tokenizers.wordtokenizer import WordTokenizer
from utils import *
#import write_csv

source_file_name = ""
collated_text = ""
archaic_words = []
modern_words = []

wt = WordTokenizer()


def built_text():
    new_collated_text=""
    char_walker = 0
    end = ""
    notes = get_notes(collated_text)
    for note in notes:
        _,end = note["span"]
        gen_text,char_walker=reform_text(note,char_walker)
        new_collated_text+=gen_text
        print(note)
    new_collated_text+=collated_text[end:]    
    return new_collated_text


def reform_text(note,char_walker):
    gen_text = ""
    modern_word = None
    _,end = note["span"]
    default_word_start_index = get_default_word_start(collated_text,note)
    alt_options = note['alt_options']
    if is_title_note(note) or not check_all_notes(note):
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
    """ if modern_word:
        write_csv.write_csv(note,modern_word,source_file_name) """
    return gen_text,char_walker


def normalize_word(word):
    puncts = ['།','་']
    for punct in puncts:
        word = word.replace(punct,"")
    return word   


def remove_particles(text):   
    tokenized_texts = wt.tokenize(text,split_affixes=True)
    particle_free_text = ""
    for tokenized_text in tokenized_texts:
        if tokenized_text.pos and tokenized_text.pos != "PART":
            particle_free_text+=tokenized_text.text    
    return particle_free_text


def get_archaic_modern_words():
    global archaic_words,modern_words
    monlam_archaics = from_yaml(Path("./res/monlam_archaics.yml"))
    lg = from_yaml(Path("./res/lekshi_gurkhang.yml"))
    archaic_words.extend(monlam_archaics)
    archaic_words.extend(lg['archaics'])
    modern_words.extend(lg['moderns'])


def is_archaic(word):
    for archaic in archaic_words:
        if normalize_word(archaic) == remove_particles(normalize_word(word)):
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
            for modern_word in modern_words:
                if remove_particles(normalize_word(option)) == normalize_word(modern_word):
                    return option
    return None



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
    #write_csv.convert_to_excel()

if __name__ == "__main__":
    text = Path("./test.txt").read_text(encoding="utf-8")
    """ new_text = resolve_archaics(text)
    Path("./gen.text").write_text(new_text) """
    notes = get_notes(text)
    for note in notes:
        print(note)
        print("********************")

    
    

