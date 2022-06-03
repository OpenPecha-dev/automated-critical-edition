import re
import logging
from typing import DefaultDict
import yaml
from antx import transfer
from openpecha.utils import dump_yaml
from gensim.models import KeyedVectors

logging.basicConfig(filename="./res/oov_list.log", level=logging.INFO)

word_vectors_path = "./res/word2vec.wordvectors"
wv = KeyedVectors.load(str(word_vectors_path), mmap='r')

def get_oov_word(error, words):
    words = {"A": words[0], "B": words[1]}
    key = str(error).split()[1].strip()[1:-1]
    return key

def find_similarity(wordA, wordB):
    try:
        sim = wv.similarity(wordA, wordB)
    except Exception as e:
        
        sim = 0.0
        oov_word = get_oov_word(e, [wordA, wordB])
        logging.info(f"{oov_word}")
        return sim

    return max([float(sim), 0.0])


def check_all_notes_option(note_options):
    for _, note in note_options.items():
        if not note:
            return False
    return True

def update_durchen(durchen, durchen_path):
    dump_yaml(durchen, durchen_path)

def update_base(opf_path, base_name, new_base):
    (opf_path / "base" / f"{base_name}.txt").write_text(new_base, encoding='utf-8')

def get_base_names(opf_path):
    base_names = []
    for base_path in list((opf_path / "base").iterdir()):
        base_names.append(base_path.stem)
    return base_names

def get_all_note_text(note_options):
    note_texts = []
    for pub, note_info in note_options.items():
        note_texts.append(note_info['note'])
    return note_texts


def get_default_note(ann_info):
    pub_mapping = {
        'པེ་': 'peking',
        'པེ': 'peking',
        'སྣར་': 'narthang',
        'སྣར': 'narthang',
        'སྡེ་': 'derge',
        'སྡེ': 'derge',
        'ཅོ་': 'chone',
        'ཅོ': 'chone'
    }
    default_key = ann_info["default"]
    default_pub = pub_mapping[default_key]
    default_note = ann_info["options"][default_pub]
    
    return default_note

def get_syls(text):
    chunks = re.split('(་|།།|།)',text)
    syls = []
    cur_syl = ''
    for chunk in chunks:
        if re.search('་|།།|།',chunk):
            cur_syl += chunk
            syls.append(cur_syl)
            cur_syl = ''
        else:
            cur_syl += chunk
    if cur_syl:
        syls.append(cur_syl)
    return syls


def get_context(chunk, type_):
    chunk = chunk.replace(':', '')
    context = ''
    syls = get_syls(chunk)
    if len(syls) >= 4:
        if type_ == 'left':
            context = f"{''.join(syls[-4:])}"
        else:
            context = f"{''.join(syls[:4])}"
    else:
        context = chunk
    return context.strip()

def clean_note(note_text):
    noise_anns = ['«པེ་»', '«སྣར་»', '«སྡེ་»', '«ཅོ་»', r'\(\d+\) ', ':']
    for noise_ann in noise_anns:
        note_text = re.sub(noise_ann, '', note_text)
    return note_text

def get_default_option(prev_chunk):
    default_option = ''
    if ':' in prev_chunk:
        default_option = re.search(':(.*)', prev_chunk,re.DOTALL).group(1)
    else:
        syls = get_syls(prev_chunk)
        if syls:
            default_option = syls[-1]
    default_option = clean_default_option(default_option)        
    return default_option

def get_note_options(default_option, note_chunk):
    note_chunk = re.sub(r'\(\d+\) ', '', note_chunk)
    z = re.match(r"<.+?(\(.+\))>",note_chunk)
    if z:
        note_chunk = note_chunk.replace(z.group(1),'')
    if "+" in note_chunk:
        default_option = ""
    note_chunk = re.sub(r"\+", "", note_chunk)
    pub_mapping = {
        '«པེ་»': 'peking',
        '«པེ»': 'peking',
        '«སྣར་»': 'narthang',
        '«སྣར»': 'narthang',
        '«སྡེ་»': 'derge',
        '«སྡེ»': 'derge',
        '«ཅོ་»': 'chone',
        '«ཅོ»': 'chone'
    }
    note_options = {
        'peking': '',
        'narthang': '',
        'derge': '',
        'chone': ''
    }
    note_parts = re.split('(«པེ་»|«སྣར་»|«སྡེ་»|«ཅོ་»|«པེ»|«སྣར»|«སྡེ»|«ཅོ»)', note_chunk)
    pubs = note_parts[1::2]
    notes = note_parts[2::2]
    for walker, (pub, note_part) in enumerate(zip(pubs, notes)):
        if note_part:
            note_options[pub_mapping[pub]] = note_part.replace('>', '')
        else:
            if notes[walker+1]:
                note_options[pub_mapping[pub]] = notes[walker+1].replace('>', '')
            else:
                note_options[pub_mapping[pub]] = notes[walker+2].replace('>', '')
    for pub, note in note_options.items():
        if "-" in note:
            note_options[pub] = ""
        if not note:
            note_options[pub] = default_option
    return note_options

def update_left_context(default_option, prev_chunk, chunk):
    left_context = re.sub(f'{default_option}$', '', prev_chunk)
    if "+" in chunk:
        left_context = prev_chunk
    return left_context

def get_alt_options(default_option,note_options):
    alt_options = []
    for note in set(note_options.values()):
        if note != default_option and note != "":
            alt_options.append(note)
    return alt_options        

def get_note_sample(prev_chunk, note_chunk, next_chunk,collated_text,prev_end):
    default_option = get_default_option(prev_chunk)
    default_option_span = (prev_end+len(prev_chunk)-len(default_option),prev_end+len(prev_chunk))
    prev_chunk = update_left_context(default_option, prev_chunk, note_chunk)
    prev_context = get_context(prev_chunk, type_= 'left')
    next_context = get_context(next_chunk, type_= 'right')
    note_options = get_note_options(default_option, note_chunk)
    note_options = dict(sorted(note_options.items()))
    alt_options = get_alt_options(default_option,note_options)
    note_span,prev_end,real_note = get_note_span(collated_text,note_chunk,prev_end)
    note = {
        "left_context":prev_context,
        "right_context":next_context,
        "default_option":default_option,
        "default_option_span":default_option_span,
        "note_options":note_options,
        "alt_options":alt_options,
        "span":note_span,
        "real_note":real_note
    }
    return note,prev_end

def get_notes(collated_text):
    cur_text_notes = []
    prev_end = 0
    chunks = re.split(r'(\(\d+\) <.+?>)', collated_text)
    prev_chunk = chunks[0]
    for chunk_walker, chunk in enumerate(chunks):
        try:
            next_chunk = chunks[chunk_walker+1]
        except:
            next_chunk = ''
        if re.search(r'\(\d+\) <.+?>', chunk):
            note,prev_end  = get_note_sample(prev_chunk, chunk, next_chunk,collated_text,prev_end)
            cur_text_notes.append(note)
            continue
        prev_chunk = chunk
    return cur_text_notes

def get_notes_samples(collated_text, note_samples, text_id):
    collated_text = collated_text.replace('\n', '')
    collated_text = re.sub(r'\d+-\d+', '', collated_text)
    cur_text_notes = get_notes(collated_text)
    for cur_text_note, note_options in cur_text_notes:
        if note_samples.get(cur_text_note, {}):
            note_samples[cur_text_note]['count'] += 1
            note_samples[cur_text_note]['text_id']=text_id
        else:
            note_samples[cur_text_note] = DefaultDict()
            note_samples[cur_text_note]['count'] = 1
            note_samples[cur_text_note]['text_id']=text_id
            note_samples[cur_text_note]['note_options'] = note_options
    return note_samples

def is_all_option_same(note_options):
    if note_options['derge'] == note_options['chone'] == note_options['peking'] == note_options['narthang']:
        return True
    else:
        return False

def get_note_context(note):
    right_context = ''
    left_context = ''
    if re.search(r'(.+)\[', note):
        left_context = re.search(r'(.+)\[', note).group(1)
    if re.search(r'\](.+)', note):
        right_context = re.search(r'\](.+)', note).group(1)
    return left_context, right_context

def get_sample_entry(note_walker, note, note_info):
    all_option_same_flag = is_all_option_same(note_info.get('note_options', {}))
    left_context, right_context = get_note_context(note)
    data_entry = [
        note_walker,
        '',
        left_context,
        note_info['note_options']['derge'],
        note_info['note_options']['chone'],
        note_info['note_options']['peking'],
        note_info['note_options']['narthang'],
        right_context,
        '',
        '',
        '',
        all_option_same_flag,
        note_info['count'],
        note_info['text_id'],
        ]
    return data_entry

def is_title_note(note):
    notes_options = []
    notes_options.append(note['note_options']['chone'])
    notes_options.append(note['note_options']['derge'])
    notes_options.append(note['note_options']['narthang'])
    notes_options.append(note['note_options']['peking'])
    
    right_context = note['right_context']
    left_context = note['left_context']
    left_context = re.sub(r"\xa0", " ", left_context)
    possible_left_texts = ["༄༅། །"]
    possible_right_texts = ["༄༅༅། །རྒྱ་གར་","༄༅། །རྒྱ་གར་","༅༅། །རྒྱ་གར་སྐད་དུ།","༄༅༅། ","༄༅༅།། །རྒྱ་གར་","ལྟར་བཀོད་ཅིང།"]
    
    
    for left_text in possible_left_texts:
        if left_text in left_context:
            return True
    for right_text in possible_right_texts:
        if right_text in right_context:
            for note_option in notes_options:
                if '༄༅།' in note_option:
                    return False
                else:
                    return True
    return False
    

def get_note_span(collated_text,chunk,prev_end):
    p = re.compile(r"\(.+?\) <.*?>")
    for m in p.finditer(collated_text):
        start,end = m.span()
        if m.group() in chunk and prev_end <= start:
            return m.span(),end,m.group()


def toyaml(dict):
    return yaml.safe_dump(dict, sort_keys=False, allow_unicode=True)

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding="utf-8"))

def get_text_id_and_vol_num(text_path):
    text_name = text_path.name[:-4]
    map = re.match(r"([A-Z][0-9]+[a-z]?)\_(v[0-9]+)",text_name)
    text_id = map.group(1)
    vol_num = map.group(2)[1:]
    return text_id, vol_num

def check_all_notes(note):
    for _, note_option in note['note_options'].items():
        if note_option == "":
            return False
        elif "!" in note_option:
            return False
    return True  


def  get_prev_note_span(notes, num):
    if num == 0:
        return None, None
    else:
        return notes[num-1]['span']

    
def get_pages(collated_text, vol_num):
    pages = re.split(f"({int(vol_num)}-[0-9]+)", collated_text)
    return pages

def resolve_title_notes(text_path):
    _, vol_num = get_text_id_and_vol_num(text_path)
    collated_text = text_path.read_text(encoding='utf-8')
    new_collated_text = ""
    pages = get_pages(collated_text, vol_num)
    page = pages[0]
    notes = get_notes(page)
    for _, note in enumerate(notes,0):
        title_check = is_title_note(note)
        if title_check:
            page = page.replace(f"{note['real_note']}", "")
    pages[0] = page
    for page_ in pages:
        new_collated_text += page_
    return new_collated_text

def clean_default_option(option):
    if re.search(r"\d+-\d+",option):
        option = re.sub(r"\d+\-\d+","",option)
    return option  

def remove_line_break(collated_text):
    text = re.sub(r"\n", "", collated_text)
    return text


def correct_shad_and_tsek_in_note(default_option, replacement_note):
    if replacement_note:
        if default_option != replacement_note:
            if replacement_note[-1:] == "།":
                if default_option[-1:] != "།":
                    corrected_note = replacement_note[:-1]+"་"
                    return corrected_note
    return replacement_note
            
def tranfer_line_break(source_text_path, target_text):
    source_text = source_text_path.read_text(encoding='utf-8')
    annotations = [['end_line', r"(\n)"]]
    result = transfer(source_text, annotations, target_text, output="txt")
    return result


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

def get_next_start(num, anns):
    if num == len(anns):
        next_start = None
    else:
        for ann_num,(_, ann_info) in enumerate(anns.items(), 1):
            if ann_num == num+1:
                next_start = ann_info['span']['start']
    return next_start


def get_base(new_durchen, old_durchen, base_text, note_type):
    new_base_text = ""
    anns = new_durchen['annotations']
    for ann_num, (ann_id, ann_info) in enumerate(anns.items(), 1):
        default_pub = ann_info['default']
        if ann_info['options'][default_pub]['features'] and note_type in ann_info['options'][default_pub]['features']:
            start = ann_info["span"]['start']
            end = old_durchen['annotations'][ann_id]['span']['end']
            note = ann_info['options'][default_pub]['note']
            next_start = get_next_start(ann_num, old_durchen['annotations'])
            if ann_num == 1:
                new_base_text += base_text[0:start] + note + base_text[end:next_start]
            elif ann_num == len(anns):
                new_base_text += note + base_text[end:]
            else:
                new_base_text += note + base_text[end:next_start]
        else:
            start = old_durchen['annotations'][ann_id]['span']['start']
            end = old_durchen['annotations'][ann_id]["span"]['end']
            note = old_durchen['annotations'][ann_id]['options'][default_pub]['note']
            next_start = get_next_start(ann_num, old_durchen['annotations'])
            if ann_num == 1:
                new_base_text += base_text[0:start] + note + base_text[end:next_start]
            elif ann_num == len(anns):
                new_base_text += note + base_text[end:]
            else:
                new_base_text += note + base_text[end:next_start]                
    return new_base_text
