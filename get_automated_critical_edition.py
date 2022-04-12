import re
from pathlib import Path
from resolve_sanskrit_notes import parse_notes_for_sanskrit_words
from resolve_archiac_notes import resolve_archiac


def update_notes_number(automated_critical_text):
  pass

def get_automated_critical_edition_text(text_path):
  collated_text = text_path.read_text(encoding='utf-8')
  default_sanskrit_resolved_text = resolve_default_sanskrit_notes(collated_text)
  automated_critcal_edition_text = resolve_archiac(default_sanskrit_resolved_text)
  final_text = update_notes_number(automated_critical_text)
