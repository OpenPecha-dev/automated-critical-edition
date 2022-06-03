import csv
from utils import get_base_names, update_durchen,toyaml
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import load_yaml
from pathlib import Path
import sqlite3


def is_alternatives(options):
    distinct_notes = has_two_distinct_notes(options)
    sqliteConnection = sqlite3.connect('./res/alternatives.sqlite')
    cursor = sqliteConnection.cursor()
    cursor.execute(f"SELECT word1,word2 FROM alt_word WHERE word1=? or word1=?",(list(distinct_notes)[0],list(distinct_notes)[1]))
    rows = cursor.fetchall()
    sqliteConnection.commit()
    cursor.close()

    if not rows:
        return False
    for row in rows:
        row_set = set(row)
        if distinct_notes.issubset(row_set):
            print(row_set)
            return True 

    return False    


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
    durchen = resolve_annotations(yml)
    new_yml = toyaml(durchen)
    Path("./res.yml").write_text(new_yml)