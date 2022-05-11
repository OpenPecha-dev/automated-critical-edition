from __future__ import annotations
from pathlib import Path
from automated_critical_edition.utils import check_all_notes_option
from botok import WordTokenizer
from openpecha.utils import load_yaml
from openpecha.core.pecha import OpenPechaFS
from automated_critical_edition.docx_serializer import get_base_names
from automated_critical_edition.utils import update_durchen

wt = WordTokenizer()

def check_for_sanskrit_syl_using_botok(note):
    tokens = wt.tokenize(note)
    tokens_len = len(tokens)
    num = 0
    for token in tokens:
        if token.skrt:
           num += 1
        elif token.chunk_type == "PUNCT":
            tokens_len -= 1
            
    if tokens_len == num or num > tokens_len/2:
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
                anns[ann_id]['options'][default_pub]['apparatus'] = ["sanskrit"]
                
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
                    anns[ann_id]['options'][default_pub]['apparatus'] = ["sanskrit"]
                
    durchen["annotations"].update(anns)
    return durchen

def resolve_sanskrit_notes(opf_path):
    pecha = OpenPechaFS(opf_path)
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        durchen_path = pecha.layers_path / base_name / "Durchen.yml"
        default_resolved_durchen = resolve_default_sanskrit_notes(durchen_layer)
        sanskrit_resolved_durchen = resolve_sanskrit_optional_notes(default_resolved_durchen)
        update_durchen(sanskrit_resolved_durchen, durchen_path)
