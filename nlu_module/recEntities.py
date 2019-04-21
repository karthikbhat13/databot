import pandas as pd
import nltk
from nltk import PorterStemmer
from nltk.corpus import wordnet as wn

def init_datababse():
        
    DATASET_PATH = "/home/karthik/databot/nlu_module/imdb-alter.csv"

    df = pd.read_csv(DATASET_PATH)

    columns = df.columns

    ps_stemmer = PorterStemmer()

    stem_columns = [(ps_stemmer.stem(s),s) for s in columns]

    return stem_columns

def wrap_convert(columns):
    verbs_to_col = {}

    for stem_column, column in columns:
        verbs = convert(stem_column, 'n', 'v')
        if(len(verbs) == 0):
            verbs_to_col[column] = []
            verbs_to_col[column].append(column)
            continue
        res_verbs = []

        res_verbs.append(column)
        for verb in verbs:
            if(verb[1] >= 0.1):
                res_verbs.append(verb[0])
        res_verbs = list(set(res_verbs))
        verbs_to_col[column] = res_verbs
    return verbs_to_col

def convert(word, from_pos, to_pos):    
	WN_NOUN = 'n'
	WN_VERB = 'v'
	WN_ADJECTIVE = 'a'
	WN_ADJECTIVE_SATELLITE = 's'
	WN_ADVERB = 'r'

	synsets = wn.synsets(word, pos=from_pos)
    # print(synsets)
    # Word not found
	if not synsets:
		return []
	# print(synsets[0].lemmas()[0].

    # Get all lemmas of the word (consider 'a'and 's' equivalent)
	lemmas = [l for s in synsets
                for l in s.lemmas() 
                if s.name().split('.')[1] == from_pos
                    or from_pos in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)
                        and s.name.split('.')[1] in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)]
	
	# print(lemmas)
    # Get related forms
	derivationally_related_forms = [(l, l.derivationally_related_forms()) for l in lemmas]
	# print(derivationally_related_forms)
    # filter only the desired pos (consider 'a' and 's' equivalent)

	related_noun_lemmas = [l for drf in derivationally_related_forms
                             for l in drf[1] 
                             if l.synset().name().split('.')[1] == to_pos
                                or to_pos in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)
                                    and l.synset().name().split('.')[1] in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)]
    # Extract the words from the lemmas
	words = [l.name() for l in related_noun_lemmas]
	len_words = len(words)
 
    # Build the result in the form of a list containing tuples (word, probability)
	result = [(w, float(words.count(w))/len_words) for w in set(words)]
	result.sort(key=lambda w: -w[1])
	
    # return all the possibilities sorted by probability
	return result
if __name__ == "__main__":
    print(wrap_convert(init_datababse()))
