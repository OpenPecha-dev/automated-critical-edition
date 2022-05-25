import re
from pathlib import Path
from automated_critical_edition.detect_archaic_notes import resolve_archaics
from automated_critical_edition.detect_sanskrit_notes import resolve_sanskrit_notes
from automated_critical_edition.detect_outlier import resolve_outlier_notes
from automated_critical_edition.detect_punctuation_note import resolve_punctuation_notes
from automated_critical_edition.detect_pedurma_mistake import resolve_pedurma_mistake_note
from automated_critical_edition.docx_serializer import opf_to_docx


def get_automated_critical_edition_text(opf_path):
  resolve_sanskrit_notes(opf_path)
  resolve_outlier_notes(opf_path)
  resolve_punctuation_notes(opf_path)
  resolve_pedurma_mistake_note(opf_path)
  # resolve_archaics(opf_path)
  opf_to_docx(opf_path, output_dir=Path("./data/docx/"))





if __name__ == "__main__":
  opf_paths = list(Path('./data/opfs').iterdir())
  opf_paths.sort()
  for opf_path in opf_paths:
    opf_path = opf_path / f"{opf_path.stem}.opf"
    get_automated_critical_edition_text(opf_path)
    print(f"{opf_path.stem} completed")