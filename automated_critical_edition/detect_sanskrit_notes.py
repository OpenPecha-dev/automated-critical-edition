from botok import WordTokenizer
from openpecha.core.pecha import OpenPechaFS
from automated_critical_edition.utils import update_durchen, get_base_names
from pathlib import Path


wt = WordTokenizer()


def update_features_for_options(ann_info, pub_types):
    for pub, info in ann_info['options'].items():
        if pub in pub_types:
            info['features'] = ["SANSKRIT"]
    return ann_info

def check_for_sanskrit_syl_using_botok(note):
    tokens = wt.tokenize(note)
    for token in tokens:
        if token.skrt:
            return True
    return False


def resolve_sanskrits(durchen):
    anns = durchen["annotations"]
    for ann_id, ann_info in anns.items():
        if ann_info["printable"] == True:
            pub_types = []
            note_options = ann_info["options"]
            for pub_type, note in note_options.items():
                if note['note'] != "":
                    if check_for_sanskrit_syl_using_botok(note['note']):
                        pub_types.append(pub_type)

            if len(pub_types) >= 1:
                anns[ann_id]["printable"] = False
                ann_info = update_features_for_options(ann_info, pub_types)
                anns[ann_id].update(ann_info)
                
    durchen["annotations"].update(anns)
    return durchen


def resolve_sanskrit_notes(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        durchen_path = pecha.layers_path / base_name / "Durchen.yml"
        sanskrit_resolved_durchen = resolve_sanskrits(durchen_layer)
        update_durchen(sanskrit_resolved_durchen, durchen_path)
