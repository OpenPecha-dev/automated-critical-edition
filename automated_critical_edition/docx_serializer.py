import re
from pathlib import Path

from pypandoc import convert_text
from openpecha.core.pecha import OpenPechaFS
from automated_critical_edition.utils import get_base_names

def get_note(durchen_ann, note_walker):
    tib_names = {
        "derge": "སྡེ་དགེ།",
        "chone": "ཅོ་ནེ།",
        "peking": "པེ་ཅིན།",
        "narthang": "སྣར་ཐང་།",
    }
    note_md = f"[^{note_walker}]:"
    default_pub = durchen_ann['default']
    default_note = durchen_ann['options'][default_pub]['note']
    alt_note = ""
    for pub, note_info in durchen_ann['options'].items():
        tib_pub = tib_names[pub]
        if note_info['note'] != default_note:
            if alt_note != note_info['note']:
                note_md += f" {note_info['note']} *{tib_pub}* "
                alt_note = note_info['note']
            else:
                note_md += f"  *{tib_pub}* "
    # note_md += "\n"
    return note_md


def reformat_collated_text(text):
    reformated_text = ""

    text = re.sub("\n", "", text)
    # text_parts = re.split("(། །)", text)
    # sentence_walker = 0
    # for text_part in text_parts:
    #     if text_part == "། །":
    #         if sentence_walker == 100:
    #             reformated_text += f"{text_part}\n"
    #             sentence_walker = 0
    #         else:
    #             reformated_text += text_part
    #             sentence_walker += 1
    #     else:
    #         reformated_text += text_part
    reformated_text = re.sub("([།གཤཀ]། ?། ?།)", "\g<1>\n\n", text)
    reformated_text = reformated_text.replace(":", "")
    return reformated_text
            

def get_collated_text_md(durchen_layer, base_text):
    collated_text_md = ""
    char_walker = 0
    note_walker = 1
    footnotes = "\n\n"
    last_durchen_ann = {}
    for uuid, durchen_ann in durchen_layer['annotations'].items():
        if durchen_ann['printable']:
            # footnotes += f"{get_note(durchen_ann, note_walker)}\n"
            footnotes += f"{get_note(durchen_ann, note_walker)}    "
            prev_chunk = base_text[char_walker:durchen_ann['span']['end']]
            collated_text_md += f"{prev_chunk}[^{note_walker}]"
            char_walker = durchen_ann['span']['end']
            note_walker += 1
            last_durchen_ann = durchen_ann
    if last_durchen_ann:
        collated_text_md += base_text[last_durchen_ann['span']['end']:]
    else:
        collated_text_md = base_text
    collated_text_md = reformat_collated_text(collated_text_md)
    collated_text_md += footnotes
    return collated_text_md


def opf_to_docx(opf_path, output_dir):
    pecha = OpenPechaFS(opf_path)
    pecha_meta = pecha.read_meta_file()
    base_names = get_base_names(opf_path)
    for base_name in base_names:
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        base_text = pecha.read_base_file(base_name)
        text_id = pecha_meta['source_metadata']['text_id']
        collated_text_md = get_collated_text_md(durchen_layer, base_text)
        output_path = output_dir / f"{text_id}_{base_name}.docx"
        convert_text(
            collated_text_md, "docx", "markdown", outputfile=str(output_path), extra_args=["-M2GB", "+RTS", "-K64m", "-RTS"]
        )
    return output_path



if __name__ == "__main__":
    opf_path = Path('./data/opfs/shanti_deva/O470B5E71/O470B5E71.opf')
    text_id = "D1118"
    output_dir = Path('./')
    opf_to_docx(opf_path, output_dir)
