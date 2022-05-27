from pathlib import Path
from pickle import TRUE
from pyexpat import features
from botok.tokenizers.wordtokenizer import WordTokenizer
from utils import from_yaml, get_base, toyaml, get_base_names, update_durchen, update_base
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import load_yaml
import csv
from copy import deepcopy


def check_alternatives(options):
    with open("./res/alternatives.csv") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if mod_options := is_alternative(row,options):
                return mod_options

    return        

        
def is_alternative(row,options):
    words = [opt_info["note"] for _,opt_info in options.items()]
    for _,opt_info in options.items():
        note = opt_info["note"]
        if row[0] == note:
            intersection = set(words).intersection(set(row))
            if len(intersection) < 2:
                return
            for _,opt_info in options.items():
                note = opt_info["note"]
                if note in row:
                    alt = "ALTERNATIVE"
                    if opt_info["features"]:
                        opt_info["features"].append(alt)
                    else:
                        opt_info["features"] = [alt]    
            return options
    return 



def resolve_annotations(durchen):
    anns = durchen['annotations']
    for _,ann_info in anns.items():
        options = ann_info['options']
        if ann_info["printable"] != True:
            continue
        if new_options := check_alternatives(options):
            is_printable = None
            ann_info["options"] = deepcopy(new_options)
            features = [opt_info["features"] for _,opt_info in new_options.items()]
            for feature in features:
                if not feature or "ALTERNATIVE" not in feature:
                    is_printable = True
                    break
            if is_printable:
                ann_info["printable"] = True
            else:
                ann_info["printable"] = False

    return durchen


def resolve_alternatives(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        base_text = pecha.read_base_file(base_name)
        durchen_layer = pecha.read_layers_file(base_name,"Durchen")
        durchen_path = pecha.layers_path / base_name / "Durchen.yml"
        alternatives_durchen = resolve_annotations(durchen_layer)
        new_base = get_base(alternatives_durchen, load_yaml(durchen_path), base_text, "alternative")
        update_durchen(alternatives_durchen, durchen_path)
        update_base(opf_path, base_name, new_base)

