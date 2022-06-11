import re
from pathlib import Path
from automated_critical_edition.detect_alternative_notes import resolve_alternatives
from automated_critical_edition.detect_archaic_notes import resolve_archaics
from automated_critical_edition.detect_sanskrit_notes import resolve_sanskrit_notes
from automated_critical_edition.detect_outlier import resolve_outlier_notes
from automated_critical_edition.detect_punctuation_note import resolve_punctuation_notes
from automated_critical_edition.detect_pedurma_mistake import resolve_pedurma_mistake_note
from automated_critical_edition.detect_similar_word import resolve_similar_notes
from automated_critical_edition.docx_serializer import opf_to_docx


def get_automated_critical_edition_text(philo, opf_path):
  resolve_sanskrit_notes(opf_path)
  print("INFO: Sanskrit notes detected")
  resolve_outlier_notes(opf_path)
  print("INFO: Outlier notes detected")
  resolve_punctuation_notes(opf_path)
  print("INFO: Punctuation notes detected")
  resolve_pedurma_mistake_note(opf_path)
  print("INFO: Pedurma mistake notes detected")
  resolve_alternatives(opf_path)
  print("INFO: Alternative notes detected")
  resolve_similar_notes(opf_path)
  print("INFO: Similar notes detected")
  # resolve_archaics(opf_path)
  opf_to_docx(opf_path, output_dir=Path(f"./data/docx//{philo}"))





if __name__ == "__main__":
  philo = "shanti_deva"
  opf_paths = list(Path(f'./data/opfs/{philo}').iterdir())
  opf_paths.sort()
  for opf_path in opf_paths:
    # if opf_path.stem == "O1DB7D939":
    #   continue
    opf_path = opf_path / f"{opf_path.stem}.opf"
    get_automated_critical_edition_text(philo, opf_path)
    print(f"{opf_path.stem} completed")