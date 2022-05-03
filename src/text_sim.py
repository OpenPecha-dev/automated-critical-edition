import configparser
from pathlib import Path
from typing import List
from sklearn.metrics.pairwise import cosine_similarity,cosine_distances

import gensim


class TextSimBase:
  """Base class for checking text similarity."""
  
  def __init__(self, config_path=Path(__file__).parent/"config.ini"):
    self.config = configparser.ConfigParser()
    self.config.read(config_path)
    self.model = self._load_model()
    
  def compare(self, source_text: str, target_text: str):
    raise NotImplementedError()
    
    
class Doc2VecTextSim(TextSimBase):
  """Check text similarity with Doc2Vec model."""
  
  def _load_model(self):
    model_path = self.config["doc2vec"]["path"]
    return gensim.models.doc2vec.Doc2Vec.load(model_path)
  
  @staticmethod
  def _preprocess(text):
    def is_punt(word):
      for punt in ["།", "།།", "༄༅"]:
          if punt in word:
              return True
      return False
    return [token for token in text.split() if token and not is_punt(token)]
  
  def _get_text_embedding(self, text):
    tokenized_text = self._preprocess(text)
    print(tokenized_text)
    return self.model.infer_vector(tokenized_text)
  
  def compare(self, source_text: str, target_text: str):
    source_text_embedding = self._get_text_embedding(source_text)
    target_text_embedding = self._get_text_embedding(target_text)
    result = cosine_similarity(
      source_text_embedding.reshape(1,-1),
      target_text_embedding.reshape(1,-1)
    )
    return result[0]
  
  
if __name__ == "__main__":
  text_sim = Doc2VecTextSim()
  sim = text_sim.compare(
    "ཡེ་ཤེས་ མེ་ ཡིས་ ཉོན་མོངས་ བསྲེག་",
    "ཡེ་ཤེས་ མེ་ ཡིས་ དྲི་མ་ སྲེག་"
  )
  print(sim)
    
