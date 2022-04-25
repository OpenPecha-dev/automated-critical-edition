import configparser
from pathlib import Path
from typing import List

from lm import LanguageModel, LSTMLanguageModel, GPT2LanguageModel, LanguageModelType


class OptionsRanker:
  """Ranks word options in a given sentence"""
  
  def __init__(self, config_path=Path(__file__).parent/"config.ini"):
    self.config = configparser.ConfigParser()
    self.config.read(config_path)
    self.lm = self._load_lm()
    
  def _load_lm(self) -> LanguageModel:
    lm_type = self.config["ranker"]["lm_type"]
    lm_path = self.config[lm_type]["path"]
    if lm_type == LanguageModelType.LSTMLanguageModel.value:
      return LSTMLanguageModel(path=lm_path)
    elif lm_type == LanguageModelType.GPT2LanguageModel.value:
      return GPT2LanguageModel(path=lm_path)
    
  def rank(self, options: List[str], left_context: List[str], right_context: List[str]) -> List[str]:
    """return `options` in ranking order"""
    ranks = []
    for option in options:
      sentence = " ".join(left_context + [option] + right_context)
      print(sentence)
      score = self.lm.score_sentence(sentence)
      ranks.append((option, score))
    return sorted(ranks, key=lambda x: x[1], reverse=True)
  
  
if __name__ == "__main__":
  ranker = OptionsRanker()
  ranks = ranker.rank(
    options=["འི", "གི", "དི"],
    left_context=["བདེ་ཆེན་", "པདྨ་",  "འཁྱིལ་བ"],
    right_context=["ཕོ་བྲང་", "ན"]
  )
  print(ranks)
  