import nltk
import logging as log
from nltk import pos_tag, ne_chunk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tree import Tree
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer
from intent_rec import Intent_classification_final 

def chunking(tag_words):
    grammar = r"""inter : {<IN>?<WDT>?<WRB>?<WP/$>?}
                intent : {<MD.?>?<PRP>?<VB.?><JJ>?<CD>?<NN.?>+<CC>?<NN.?>?}"""

    parser = nltk.RegexpParser(grammar)
    chunked = parser.parse(tag_words)

    # print(chunked)
    # for subtree in chunked.subtrees(filter=lambda t: t.label() == 'intent'):
        # print(subtree.label())
    intent_text = ''
    inter_text = ''
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'intent'):
        intent_text = " ".join([text for text, pos in subtree.leaves()])
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'inter'):
        inter_text = " ".join([text for text, pos in subtree.leaves()])
    
    rest = []
    for chunk in chunked:
        if type(chunk) != Tree:
            rest.append(chunk[0])
    query_text = " ".join(rest)
    # log.info(intent_text)
    print("Intent text is " + intent_text)
    print("Intermediate text is " + inter_text) 
    print("query is " + query_text)
    return intent_text, inter_text, query_text


def chunkIntent(tag_words):

    grammar = r"""intent : {<MD.?>?<PRP>?<VB.?><JJ>?<CD>?<NN.?>+<CC>?<NN.?>?}"""
    parser = nltk.RegexpParser(grammar)
    chunked = parser.parse(tag_words)

    print(chunked)
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Chunk'):
        print(subtree)

def groupNounVerb(tag_words):
    proper_nouns = []
    verbs = []
    nouns = []

    proper_nouns = get_continuous_chunks(tag_words)

    is_noun = lambda pos : pos[:2] == 'NN'
    

    for word, pos in tag_words:
        if pos.startswith('V'):
            verbs.append(word)
        if is_noun(pos):
            nouns.append(word)

    split_proper_nouns = []
    for proper_noun in proper_nouns:
        split_proper_nouns += proper_noun.split()
    
    temp_nouns = [noun for noun in nouns if noun not in split_proper_nouns]
    nouns = temp_nouns
    return nouns, proper_nouns, verbs


def filter(sentence):
    log.info(sentence)
    words = word_tokenize(sentence)

    # filtered_words = remove_stopwords(words)
    tag_words = tagging(words)
    print(tag_words)
    nouns, proper_nouns, verbs = groupNounVerb(tag_words)
    split_input = []
    split_input = chunking(tag_words)
    # print(Intent_classification_final.predict(split_input[0]))
    print(nouns)
    print(proper_nouns)
    print(verbs)

def remove_stopwords(words):
    stop_words = list(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]    
    return filtered_words

def tagging(words):
    return pos_tag(words)

def get_continuous_chunks(tagged_words):
    chunked = ne_chunk(tagged_words)
    # print(chunked)
    continuous_chunk = []
    current_chunk = []

    for i in chunked:
        if type(i) == Tree:
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue

    if continuous_chunk:
        named_entity = " ".join(current_chunk)
        if named_entity not in continuous_chunk:
            continuous_chunk.append(named_entity)

    return continuous_chunk
    


if __name__ == "__main__":
    # print(filter("Barack Obama is the president of Italy"))
    # print(filter("Get all Tom Hardy's movies."))    
    # print(filter("WASHINGTON -- In the wake of a string of abuses by New York police officers in the 1990s, Loretta E. Lynch, the top federal prosecutor in Brooklyn, spoke forcefully about the pain of a broken trust that African-Americans felt and said the responsibility for repairing generations of miscommunication and mistrust fell to law enforcement."))    
    print(filter("can you get three movies in which Tom Hardy is the actor and Will is the director"))
    # print(filter("I want sudent marks  where year is 2017"))