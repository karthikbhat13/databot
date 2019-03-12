#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/Dark-Sied/Intent_Classification/blob/master/Intent_classification_final.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>


import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.lancaster import LancasterStemmer
import nltk
import re
from sklearn.preprocessing import OneHotEncoder
import matplotlib.pyplot as plt
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM, Bidirectional, Embedding, Dropout
from keras.callbacks import ModelCheckpoint
from sklearn.model_selection import train_test_split




def load_dataset(filename):
  df = pd.read_csv(filename, encoding = "latin1", names = ["Sentence", "Intent"])
  print(df.head())
  intent = df["Intent"]
  unique_intent = list(set(intent))
  sentences = list(df["Sentence"])
  
  return (intent, unique_intent, sentences)
  


def cleaning(sentences):
  words = []
  for s in sentences:
    clean = re.sub(r'[^ a-z A-Z 0-9]', " ", s)
    w = word_tokenize(clean)
    #stemming
    words.append([i.lower() for i in w])
    
  return words  


def create_tokenizer(words, filters = '!"#$%&()*+,-./:;<=>?@[\]^_`{|}~'):
  token = Tokenizer(filters = filters)
  token.fit_on_texts(words)
  print(token)
  return token


def max_length(words):
  return(len(max(words, key = len)))
  


def encoding_doc(token, words):
  return(token.texts_to_sequences(words))


def padding_doc(encoded_doc, max_length):
  return(pad_sequences(encoded_doc, maxlen = max_length, padding = "post"))


def one_hot(encode):
  o = OneHotEncoder(sparse = False)
  return(o.fit_transform(encode))

def create_model(vocab_size, max_length):
  model = Sequential()
  model.add(Embedding(vocab_size, 128, input_length = max_length, trainable = False))
  model.add(Bidirectional(LSTM(128)))
#   model.add(LSTM(128))
  model.add(Dense(32, activation = "relu"))
  model.add(Dropout(0.5))
  model.add(Dense(21, activation = "softmax"))
  
  return model




def predictions(text, word_tokenizer):
  clean = re.sub(r'[^ a-z A-Z 0-9]', " ", text)
  test_word = word_tokenize(clean)
  test_word = [w.lower() for w in test_word]
  test_ls = word_tokenizer.texts_to_sequences(test_word)
  print(test_word)
  #Check for unknown words
  if [] in test_ls:
    test_ls = list(filter(None, test_ls))
    
  test_ls = np.array(test_ls).reshape(1, len(test_ls))
 
  x = padding_doc(test_ls, max_length)
  
  pred = model.predict_proba(x)
    
  return pred

def get_final_output(pred, classes):
  predictions = pred[0]
 
  classes = np.array(classes)
  ids = np.argsort(-predictions)
  classes = classes[ids]
  predictions = -np.sort(-predictions)
 
  for i in range(pred.shape[1]):
    print("%s has confidence = %s" % (classes[i], (predictions[i])))




def train(data_file):
  intent, unique_intent, sentences = load_dataset(data_file)

  #define stemmer
  # stemmer = LancasterStemmer()

  cleaned_words = cleaning(sentences)
  # print(len(cleaned_words))
  # print(cleaned_words[:2])  
    

  word_tokenizer = create_tokenizer(cleaned_words)
  vocab_size = len(word_tokenizer.word_index) + 1
  # print(word_tokenizer.word_index)
  max_length = max_length(cleaned_words)

  print("Vocab Size = %d and Maximum length = %d" % (vocab_size, max_length))


  encoded_doc = encoding_doc(word_tokenizer, cleaned_words)
  # print(encoded_doc)

  padded_doc = padding_doc(encoded_doc, max_length)


  print("Shape of padded docs = ",padded_doc.shape)

  #tokenizer with filter changed
  output_tokenizer = create_tokenizer(unique_intent, filters = '!"#$%&()*+,-/:;<=>?@[\]^`{|}~')


  encoded_output = encoding_doc(output_tokenizer, intent)
  # print(encoded_output)

  encoded_output = np.array(encoded_output).reshape(len(encoded_output), 1)

  output_one_hot = one_hot(encoded_output)

  train_X, val_X, train_Y, val_Y = train_test_split(padded_doc, output_one_hot, shuffle = True, test_size = 0.2)

  print("Shape of train_X = %s and train_Y = %s" % (train_X.shape, train_Y.shape))
  print("Shape of val_X = %s and val_Y = %s" % (val_X.shape, val_Y.shape))


  model = create_model(vocab_size, max_length)

  model.compile(loss = "categorical_crossentropy", optimizer = "adam", metrics = ["accuracy"])
  model.summary()

  filename = 'model.h5'
  checkpoint = ModelCheckpoint(filename, monitor='val_loss', verbose=1, save_best_only=True, mode='min')

  hist = model.fit(train_X, train_Y, epochs = 100, batch_size = 32, validation_data = (val_X, val_Y), callbacks = [checkpoint])

  return model


def predict(text):
  intent, unique_intent, sentences = load_dataset("/home/karthik/databot/nlu_module/intent_rec/Dataset.csv")
  
  cleaned_words = cleaning(sentences)

  word_tokenizer = create_tokenizer(cleaned_words)
  model = load_model("/home/karthik/databot/nlu_module/intent_rec/model.h5")
  pred = predictions(text, word_tokenizer)
  get_final_output(pred, unique_intent)
