import re
from typing import DefaultDict


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
    noise_anns = ['«པེ་»', '«སྣར་»', '«སྡེ་»', '«ཅོ་»', '\(\d+\) ', ':']
    for noise_ann in noise_anns:
        note_text = re.sub(noise_ann, '', note_text)
    return note_text

def get_default_option(prev_chunk):
    default_option = ''
    if ':' in prev_chunk:
        default_option = re.search(':(.*)', prev_chunk).group(1)
    else:
        syls = get_syls(prev_chunk)
        if syls:
            default_option = syls[-1]
    return default_option

def get_note_options(default_option, note_chunk):
    note_chunk = re.sub('\(\d+\)', '', note_chunk)
    if "+" in note_chunk:
        default_option = ""
    note_chunk = re.sub("\+", "", note_chunk)
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

def get_note_sample(prev_chunk, note_chunk, next_chunk):
    note_sample = ''
    default_option = get_default_option(prev_chunk)
    prev_chunk = update_left_context(default_option, prev_chunk, note_chunk)
    prev_context = get_context(prev_chunk, type_= 'left')
    next_context = get_context(next_chunk, type_= 'right')
    note_options = get_note_options(default_option, note_chunk)
    note_options = dict(sorted(note_options.items()))
    alt_options = get_alt_options(default_option,note_options)
    #note_sample = f'{prev_context}[{",".join(str(note) for note in note_options.values())}]{next_context}'
    note = {
        "left_context":prev_context,
        "right_context":next_context,
        "default_option":default_option,
        "note_options":note_options,
        "alt_options":alt_options
    }
    return note

def parse_notes(collated_text):
    cur_text_notes = []
    chunks = re.split('(\(\d+\) <.+?>)', collated_text.replace("\n",""))
    prev_chunk = chunks[0]
    for chunk_walker, chunk in enumerate(chunks):
        try:
            next_chunk = chunks[chunk_walker+1]
        except:
            next_chunk = ''
        if re.search('\(\d+\) <.+?>', chunk):
            note  = get_note_sample(prev_chunk, chunk, next_chunk)
            cur_text_notes.append(note)
            continue
        prev_chunk = chunk
    return cur_text_notes

def get_notes_samples(collated_text, note_samples, text_id):
    collated_text = collated_text.replace('\n', '')
    collated_text = re.sub('\d+-\d+', '', collated_text)
    cur_text_notes = parse_notes(collated_text)
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
    possible_right_texts = ["༄༅། །"]
    possible_left_texts = ["༄༅༅། །རྒྱ་གར་","༄༅། །རྒྱ་གར་","༅༅། །རྒྱ་གར་སྐད་དུ།","༄༅༅། ","༄༅༅།། །རྒྱ་གར་","ལྟར་བཀོད་ཅིང།"]
    
    
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

def get_notes_with_span(collated_text):
    notes = []
    p = re.compile("\(.+?\)\s*<.*?>")
    for m in p.finditer(collated_text):
        notes.append({"note":m.group(),"span":m.span()})
    return notes


def get_default_word(collated_text,end_index):
    index = end_index-1
    start_index = ""
    while index > 0:
        if collated_text[index] == ":":
            start_index =  index+1
            break
        elif re.search("\s",collated_text[index]):
            index_in = end_index-2
            while collated_text[index_in] not in ["་","།","\n"]:
                index_in-=1
            start_index = index_in+1
            break
        index-=1
    return collated_text[start_index:end_index],start_index

def get_notes(collated_text):
    """this function gives the notes of the collated text
       as return

    Args:
        text_path (string): path to the collated_text

    Returns:
        list: list containing all the notes of the current collated text
    """
    notes_for_context = parse_notes(collated_text)
    notes_with_span = get_notes_with_span(collated_text)
    return notes_with_span, notes_for_context
        
