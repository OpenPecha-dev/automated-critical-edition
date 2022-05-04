import re
from pathlib import Path

from pypandoc import convert_text
from openpecha.core.pecha import OpenPechaFS

def get_note(durchen_ann, note_walker):
    tib_names = {
        "derge": "སྡེ་དགེ།",
        "chone": "ཅོ་ནེ།",
        "peking": "པེ་ཅིན།",
        "narthang": "སྣར་ཐང་།",
    }
    note_md = f"[^{note_walker}]:"
    default_pub = durchen_ann['default']
    default_note = durchen_ann['options'][default_pub]
    alt_note = ""
    for pub, note in durchen_ann['options'].items():
        tib_pub = tib_names[pub]
        if note != default_note:
            if alt_note != note:
                note_md += f" {note} *{tib_pub}* "
                alt_note = note
            else:
                note_md += f" *{tib_pub}* "
    note_md += "\n"
    return note_md


def reformat_collated_text(text):
    reformated_text = ""
    text = re.sub("\n", "", text)
    text_parts = re.split("(། །)", text)
    sentence_walker = 0
    for text_part in text_parts:
        if text_part == "། །":
            if sentence_walker == 100:
                reformated_text += f"{text_part}\n"
                sentence_walker = 0
            else:
                reformated_text += text_part
                sentence_walker += 1
        else:
            reformated_text += text_part
    reformated_text = reformated_text.replace(":", "")
    return reformated_text
            

def get_collated_text_md(durchen_layer, base_text):
    collated_text_md = ""
    char_walker = 0
    note_walker = 1
    footnotes = "\n\n"
    for uuid, durchen_ann in durchen_layer['annotations'].items():
        if durchen_ann['printable']:
            footnotes += f"{get_note(durchen_ann, note_walker)}\n"
            prev_chunk = base_text[char_walker:durchen_ann['span']['end']]
            collated_text_md += f"{prev_chunk}[^{note_walker}]"
            char_walker = durchen_ann['span']['end']
            note_walker += 1
            last_durchen_ann = durchen_ann
    collated_text_md += base_text[last_durchen_ann['span']['end']:]
    collated_text_md = reformat_collated_text(collated_text_md)
    collated_text_md += footnotes
    return collated_text_md

def opf_to_docx(opf_path, output_dir, text_id):
    pecha = OpenPechaFS(opf_path)
    durchen_layer = pecha.read_layers_file("00001", "Durchen")
    base_text = pecha.read_base_file("00001")
    collated_text_md = get_collated_text_md(durchen_layer, base_text)
    output_path = output_dir / f"{text_id}_format_namgyal.docx"
    convert_text(
        collated_text_md, "docx", "markdown", outputfile=str(output_path)
    )
    return output_path



if __name__ == "__main__":
    opf_path = Path('./demo_opf/PFCFAE7FE/PFCFAE7FE.opf')
    text_id = "D1118"
    output_dir = Path('./demo_opf')
    opf_to_docx(opf_path, output_dir, text_id)
