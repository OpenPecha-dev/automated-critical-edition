from __future__ import annotations
from pathlib import Path
from automated_critical_edition.utils import *
from botok.third_party.has_skrt_syl import has_skrt_syl
from botok import WordTokenizer
from openpecha.utils import load_yaml

wt = WordTokenizer()

def check_for_sanskrit_syl_using_botok(note):
    tokens = wt.tokenize(note)
    for token in tokens:
        if token.skrt:
            return True
    return False


def resolve_default_sanskrit_notes(durchen):
    """it parse all the notes of the collated text
        to check if they are sanskrit words

    Args:
        list (string): list of notes
    """
    anns = durchen["annotations"]
    for ann_id, ann_info in anns.items():
        note_options = ann_info["options"]
        all_notes = check_all_notes_option(note_options)
        if all_notes:
            default_note = get_default_note(ann_info)
            if has_skrt_syl(default_note) or check_for_sanskrit_syl_using_botok(default_note):
                anns[ann_id]["printable"] = False
                print(anns[ann_id])
                
    durchen["annotations"].update(anns)
    return durchen

def resolve_sanskrit_optional_notes(durchen):
    anns = durchen["annotations"]
    for ann_id, ann_info in anns.items():
        if ann_info["printable"] == True:
            notes = []
            note_options = ann_info["options"]
            all_notes = check_all_notes_option(note_options)
            if all_notes:
                for _, note in note_options.items():
                    if has_skrt_syl(note) or check_for_sanskrit_syl_using_botok(note):
                        notes.append(note)
                if len(notes) >= 2:
                    anns[ann_id]["printable"] = False
                    print(anns[ann_id])
                
    durchen["annotations"].update(anns)
    return durchen


def resolve_sanskrit_notes(opf_path):
    layers_path = opf_path / "layers"
    vol_paths = list(Path(layers_path).iterdir())
    for vol_path in vol_paths:
        durchen_path = Path(f"{vol_path}/Durchen.yml")
        durchen = load_yaml(durchen_path)
        default_resolved_durchen = resolve_default_sanskrit_notes(durchen)
        sanskrit_resolved_durchen = resolve_sanskrit_optional_notes(default_resolved_durchen)
        update_durchen(sanskrit_resolved_durchen, durchen_path)
        
    return durchen_path