import re

from pathlib import Path

from openpecha.core.pecha import OpenPechaFS
from automated_critical_edition.utils import get_base_names

def get_left_context(base_text, annotation):
    annotation_start = annotation['span']['start']
    left_context = base_text[annotation_start-20:annotation_start]
    left_context = left_context.replace("\n" ,"")
    return left_context

def get_right_context(base_text, annotation):
    annotation_end = annotation['span']['end']
    try:
        right_context = base_text[annotation_end:annotation_end+20]
    except:
        right_context = base_text[annotation_end:]
    right_context = right_context.replace("\n" ,"")
    return right_context

def get_resolve_method(note_options):
    methods = []
    for pub, note_option in note_options.items():
        if note_option['features']:
            if note_option['features'] == "SIMILAR":
                methods.append("SIMILAR")
                continue
            for feat in note_option['features']:
                methods.append(feat)
    resolve_methods = ""
    for method in set(methods):
        resolve_methods += f"{method}/"
    return resolve_methods


def parse_printable_false(base_text, durchen_layer):
    printable_false_notes = ""
    for uuid, annotation in durchen_layer['annotations'].items():
        if not annotation['printable']:
            left_context = get_left_context(base_text, annotation)
            right_context = get_right_context(base_text, annotation)
            default_pub = annotation['default']
            decision_note = annotation['options'][default_pub]['note']
            derge_text = annotation['options']['derge']['note']
            chone_text = annotation['options']['chone']['note']
            narthang_text = annotation['options']['narthang']['note']
            peking_text = annotation['options']['peking']['note']
            method = get_resolve_method(annotation['options'])
            printable_false_notes += f"{uuid},{left_context},{derge_text},{chone_text},{narthang_text},{peking_text},{right_context},{decision_note},{method}\n"

    return printable_false_notes


def get_text_report(opf_path):
    text_report = "Annotation Id, Left Context, Derge, Chone, Narthang, Peking, Right Context, Decision, Method\n"
    pecha = OpenPechaFS(opf_path)
    pecha_path = pecha.opf_path
    base_names = get_base_names(pecha_path)
    for base_name in base_names:
        base_text = pecha.read_base_file(base_name)
        durchen_layer = pecha.read_layers_file(base_name, "Durchen")
        text_report += parse_printable_false(base_text, durchen_layer)
    return pecha.meta.source_metadata['text_id'], text_report


if __name__ == "__main__":
    opf_paths  = list(Path('./data/opfs').iterdir())
    opf_paths = [Path('./data/opfs/shanti_deva/O1DB7D939')]
    for opf_path in opf_paths:
        opf_id = opf_path.stem
        text_id, text_report = get_text_report(opf_path)
        Path(f'./data/text_report/{text_id}_{opf_id}.csv').write_text(text_report, encoding='utf-8')
