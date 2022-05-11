from __future__ import annotations
from pathlib import Path
from automated_critical_edition.utils import check_all_notes_option
from botok import WordTokenizer
from botok.third_party.has_skrt_syl import has_skrt_syl
from openpecha.utils import load_yaml

wt = WordTokenizer()

def update_apparatus(ann_info):
    default = ann_info['default']
    if ann_info["options"][default]['apparatus']:
        curr_apparatus = [ann_info["options"][default]['apparatus']]
    else:
        curr_apparatus = []
    curr_apparatus.append("SANSKRIT")
    ann_info['options'][default]['apparatus'] = curr_apparatus
    return ann_info

def check_for_sanskrit_syl_using_botok(note):
    tokens = wt.tokenize(note)
    tokens_len = len(tokens)
    num = 0
    for token in tokens:
        if token.skrt:
            # return True
           num += 1
        elif token.chunk_type == "PUNCT":
            tokens_len -= 1
            
    if tokens_len == num or num >= tokens_len/2:
        return True
    else:
        return False


def resolve_default_sanskrit_notes(durchen):
    anns = durchen["annotations"]
    for ann_id, ann_info in anns.items():
        note_options = ann_info["options"]
        default_pub = ann_info['default']
        all_notes = check_all_notes_option(note_options)
        if all_notes:
            default_note = ann_info['options'][default_pub]['note']
            if check_for_sanskrit_syl_using_botok(default_note):
                anns[ann_id]["printable"] = False
                ann_info = update_apparatus(ann_info)
                anns[ann_id].update(ann_info)
    durchen["annotations"].update(anns)
    return durchen

def resolve_sanskrit_optional_notes(durchen):
    anns = durchen["annotations"]
    for ann_id, ann_info in anns.items():
        if ann_info["printable"] == True:
            pub_types = []
            note_options = ann_info["options"]
            all_notes = check_all_notes_option(note_options)
            default_pub = ann_info['default']
            if all_notes:
                for pub_type, note in note_options.items():
                    if pub_type != default_pub:
                        if check_for_sanskrit_syl_using_botok(note['note']):
                            pub_types.append(pub_type)
                if len(pub_types) >= 1:
                    anns[ann_id]["printable"] = False
                    ann_info = update_apparatus(ann_info)
                    anns[ann_id].update(ann_info)
                
    durchen["annotations"].update(anns)
    return durchen

def resolve_sanskrit_notes(layers_path):
    vol_paths = list(Path(layers_path).iterdir())
    for vol_path in vol_paths:
        durchen_path = Path(f"{vol_path}/Durchen.yml")
        durchen = load_yaml(durchen_path)
        default_resolved_durchen = resolve_default_sanskrit_notes(durchen)
        sanskrit_resolved_durchen = resolve_sanskrit_optional_notes(default_resolved_durchen)
    return sanskrit_resolved_durchen
