from openpecha.utils import dump_yaml



def check_all_notes_option(note_options):
    for _, note in note_options.items():
        if note['note'] == "":
            return False
        elif "!" in note['note']:
            return False
    return True

def update_durchen(durchen, durchen_path):
    dump_yaml(durchen, durchen_path)

def update_durchen_offset(offset, anns, _id):
    start_ann = int(anns[_id]['span']['start'])
    for ann_id, ann_info in anns.items():
        start = int(ann_info['span']['start'])
        end = int(ann_info['span']['end'])
        if start_ann <= start:
            if _id == ann_id:
                ann_info['span']['end'] = int(end + offset)
            else:
                ann_info['span']['start'] = int(start + offset)
                ann_info['span']['end'] = int(end + offset)
    return anns

def get_diff_dic(durchen):
    curr_dic = {}
    diff_dic = {}
    anns = durchen['annotations']
    for ann_id, ann_info in anns.items():
        curr_dic[ann_id]= {
            "diff": int(ann_info['span']['end']) - int(ann_info['span']['start'])
        }
        diff_dic.update(curr_dic)
        curr_dic = {}
    return diff_dic


def get_base(new_durchen, old_durchen, base_text, note_type):
    diff_dic = get_diff_dic(old_durchen)
    anns = new_durchen['annotations']
    for ann_id, ann_info in anns.items():
        if ann_info['printable'] == False:
            default_pub = ann_info['default']
            if note_type in ann_info['options'][default_pub]['apparatus']:
                start = ann_info["span"]['start']
                end = int(start + diff_dic[ann_id]['diff'])
                note = ann_info['options'][default_pub]['note']
                base_text = base_text[0:start] + note + base_text[end:]
    return base_text
