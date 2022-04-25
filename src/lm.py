from enum import Enum
import pickle
from pathlib import Path


import numpy as np
import tensorflow as tf

class LanguageModelType(str, Enum):
  LSTMLanguageModel = "lstm_lm"
  GPT2LanguageModel = "gpt2_lm"


class LanguageModel:
  def score_sentence(sentence):
    raise NotImplementedError()

class LSTMLanguageModel(LanguageModel):
  
  def __init__(self, path):
    self.model, self.tokenizer = self.load_model(Path(path))
    self.vocab_inv = {v: k for k, v in self.tokenizer.word_index.items()}
    
  @property
  def input_length(self):
    self.model.layers[0].input_length
  
  @staticmethod
  def save_model(path, model, tokenizer=None):
    model.save(path)
    if tokenizer:
      pickle.dump(tokenizer, (path / 'tokenizer.pkl').open('wb'))
    return path
  
  @staticmethod
  def load_model(path):
    model = tf.keras.models.load_model(path)
    tokenizer = pickle.load((path / 'tokenizer.pkl').open('rb'))
    return model, tokenizer
  
  @staticmethod
  def generate_xy_pairs(seq, max_len):
    x, y = [], []
    for i, tok_id in enumerate(seq):
      x_padded = tf.keras.preprocessing.sequence.pad_sequences([seq[:i]], maxlen=max_len)[0]
      x.append(x_padded)
      y.append(tok_id)
    return x, y

  def score_sentence(self, sentence):
    seq = self.tokenizer.texts_to_sequences([sentence])[0]
    x_test, y_test = self.generate_xy_pairs(seq, self.input_length)
    print(x_test)
    x_test = np.array(x_test)
    y_test = np.array(y_test)
    p_pred = self.model.predict(x_test)
    log_p_sentence = 0
    for i, prob in enumerate(p_pred):
      word = self.vocab_inv[y_test[i]] 
      history = ' '.join([vocab_inv[w] for w in x_test[i, :] if w != 0])
      prob_word = prob[y_test[i]]
      log_p_sentence += np.log(prob_word)
      # print('P(w={}|h={})={}'.format(word, history, prob_word))
    # print('Prob. sentence: {}'.format(np.exp(log_p_sentence))
    return np.exp(log_p_sentence)
  

class GPT2LanguageModel(LanguageModel):
  
  def score_sentence(sentence):
    print("coming soon")
    return []
          