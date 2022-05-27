import csv

from automated_critical_edition.utils import get_base_names, update_durchen
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import load_yaml
from pathlib import Path


def is_alternatives(options):
    with open("./res/alternatives.csv") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if check_alternative(row,options):
                return True

        
def check_alternative(row,options):
    distinct_notes = has_two_distinct_notes(options)
    row_set = set(row)
    if distinct_notes.issubset(row_set):
        return True  


def has_two_distinct_notes(options):
    note_set = set()
    for val in options.values():
        note_set.add(val["note"])
    if len(note_set) == 2:
        return note_set   



def resolve_annotations(durchen):
    anns = durchen['annotations']
    for _,ann_info in anns.items():
        options = ann_info['options']
        if ann_info["printable"] == True and has_two_distinct_notes(options):
            if not is_alternatives(options):
                continue
            ann_info["printable"] = False
            for val in options.values():
                val["features"] = val["features"].append("ALTERNATIVE") if val["features"] != None else ["ALTERNATIVE"]

    return durchen


def resolve_alternatives(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        durchen_layer = pecha.read_layers_file(base_name,"Durchen")
        durchen_path = pecha.layers_path / base_name / "Durchen.yml"
        alternatives_durchen = resolve_annotations(durchen_layer)
        update_durchen(alternatives_durchen, durchen_path)


if __name__ == "__main__":
    test_file = Path("./tests/alternative_notes/data/input_durchen.yml")
    yml = load_yaml(test_file)
    resolve_annotations(yml)