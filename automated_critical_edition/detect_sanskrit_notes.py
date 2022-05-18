from automated_critical_edition.utils import check_all_notes_option
from botok import WordTokenizer
from openpecha.core.pecha import OpenPechaFS
from automated_critical_edition.utils import update_durchen, get_base_names

wt = WordTokenizer()

def update_features(ann_info):
    default = ann_info['default']
    if ann_info["options"][default]['features']:
        curr_features = [ann_info["options"][default]['features']]
    else:
        curr_features = []
    if "SANSKRIT" not in curr_features:
        curr_features.append("SANSKRIT")
    ann_info['options'][default]['features'] = curr_features
    return ann_info

def check_for_sanskrit_syl_using_botok(note):
    tokens = wt.tokenize(note)
    for token in tokens:
        if token.skrt:
            return True
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
                ann_info = update_features(ann_info)
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
                    ann_info = update_features(ann_info)
                    anns[ann_id].update(ann_info)
                
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
