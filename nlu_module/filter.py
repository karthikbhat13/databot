import nltk
import logging as log
from nltk import pos_tag, ne_chunk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tree import Tree
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer
import recEntities
from fuzzywuzzy import fuzz, process
import parse_tree
import db_handler
import util
import retry
import info


def recColoumns_temp(query_text):
    query_text_words = query_text.split()

    stem_columns = recEntities.init_datababse()
    # print(stem_columns)

    verb_to_col = recEntities.wrap_convert(stem_columns)

    print(verb_to_col)
    print("\n\n")
    matched_words_col = {}
    # for col, col_var in verb_to_col.items():
    #     for word in col_var:
    #         res = process.extractOne(word, query_text_words)
    #         if(res[1] > 70):
    #             print("Column is " + col)
    #             print("Matched word is " + res[0])
    #             print("With accuracy " + str(res[1]))
    #             matched_words_col[res[0]] = col
    #             print("\n\n")

    for word in query_text_words:
        max_acc = 0
        col_mat = ''
        for col, col_var in verb_to_col.items():
            res = process.extractOne(word, col_var)
            if(res[1] > 70):
                print("word is "+word)
                print("Column is " + col)
                print("Matched word is " + res[0])
                print("With accuracy " + str(res[1]))
                if(res[1] > max_acc):
                    print(res[1], max_acc, col, col_mat)
                    max_acc = res[1]
                    col_mat = col
                print("\n\n")
        if(col_mat == ''):
            continue
        matched_words_col[word] = col_mat
    return matched_words_col

def recColoumns(query_text):
    if 'movie' in query_text:
        query_text.replace('movie', 'title')
    if 'movies' in query_text:
        query_text.replace('movies', 'title')

    query_text_words = query_text.split()

    stem_columns = recEntities.init_datababse()
    # print(stem_columns)

    verb_to_col = recEntities.wrap_convert(stem_columns)

    print(verb_to_col)
    print("\n\n")
    matched_words_col = {}
    for col, col_var in verb_to_col.items():
        for word in col_var:
            res = process.extractOne(word, query_text_words)
            if(res[1] > 70):
                print("Column is " + col)
                print("Matched word is " + res[0])
                print("With accuracy " + str(res[1]))
                matched_words_col[res[0]] = col
                print("\n\n")
    return matched_words_col

def get_relationship(query_text, intent_info):
    str_parse_tree = parse_tree.get_parse_tree(query_text)
    matched_words_col = recColoumns_temp(query_text)

    if not matched_words_col:
        rows = retry.no_col_match(query_text)
        if rows:
            rows = [row.tolist() for row in rows]
            print(rows)
            return [rows]

    
    print(str_parse_tree)
    print(matched_words_col)
    db_inp_dic = {}
    col_type, col_pos = util.get_col_pos()
    print(col_pos)
    adj_dic = util.get_adj(query_text)
    rows = []
    for key, value in matched_words_col.items():
        pos_tag = col_pos[value]

        node, val = parse_tree.get_relation(str_parse_tree, key, pos_tag)

        print("\n\n\n\n")
        print(node)
        print("\n\n\n\n")
        print(val)

        if(val != False and val is not None):
            db_inp_dic[value.lower()] = val
                     
            print(db_inp_dic)

            rows.append(db_handler.db_select(db_inp_dic, intent_info, col_type, adj_dic))
            print(rows)
        else:
            matched_rows = retry.retry(value, query_text)
            
            rows.append( [row.tolist() for row in matched_rows])
            print(rows)
    return rows

def get_intent_col(text):
    matched_words_col = recColoumns_temp(text)
    print('matched_words_col')
    
    print(matched_words_col)
    if not matched_words_col:
        return ['Title']
    elif 'movie' in text or 'movies' in text:
        return ['Title']
    cols = [val for key, val in matched_words_col.items()]
    return cols

def get_intent_info(query_text):
    intent = util.get_intent(query_text)
    
    for key, val in intent.items():
        if val:
            query_text = query_text.replace(key, '')
    cols = get_intent_col(query_text)

    number = util.get_number(query_text)

    
    intent_info = {'cols':cols, 'number':number, 'intent':intent}

    return intent_info

def chunking(tag_words):
    # grammar = r"""inter : {<IN>?<WDT>?<WRB>?<WP/$>?}
    #             intent : {<MD.?>?<PRP>?<VB.?><JJ>?<CD>?<NN.?>+<CC>?<NN.?>?}"""

    grammar = r"""inter : {<IN>?<WDT>?<WRB>?<WP/$>?}"""

    parser = nltk.RegexpParser(grammar)
    chunked = parser.parse(tag_words)

    # print(chunked)
    # for subtree in chunked.subtrees(filter=lambda t: t.label() == 'intent'):
        # print(subtree.label())
    intent_text = ''
    inter_text = ''
    # for subtree in chunked.subtrees(filter=lambda t: t.label() == 'intent'):
    #     intent_text = " ".join([text for text, pos in subtree.leaves()])
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'inter'):
        inter_text = " ".join([text for text, pos in subtree.leaves()])
    
    q = []
    i = []
    f = True
    for chunk in chunked:
        if type(chunk) != Tree:
            if f:
                i.append(chunk[0])
            else:
                q.append(chunk[0])
        else:
            f = False
    
    query_text = " ".join(q)
    intent_text = " ".join(i)
    # log.info(intent_text)
    print("Intent text is ---" + intent_text)
    print("Intermediate text is ---" + inter_text) 
    print("query is ---" + query_text)
    print("\n\n\n\n\n")
    return intent_text, inter_text, query_text


def chunkIntent(tag_words):

    grammar = r"""intent : {<MD.?>?<PRP>?<VB.?><JJ>?<CD>?<NN.?>+<CC>?<NN.?>?}"""
    parser = nltk.RegexpParser(grammar)
    chunked = parser.parse(tag_words)

    # print(chunked)
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
    words = word_tokenize(sentence)

    # filtered_words = remove_stopwords(words)
    tag_words = tagging(words)
    # print(tag_words)
    nouns, proper_nouns, verbs = groupNounVerb(tag_words)
    split_input = []
    split_input = chunking(tag_words)
    # print(Intent_classification_final.predict(split_input[0]))
    print("\n\n\n")
    print("nouns " + str(nouns))
    print("proper nouns " + str(proper_nouns))
    print("verbs " + str(verbs))
    print("\n\n\n")
    intent_info = get_intent_info(split_input[0])
    rows = get_relationship(split_input[2], intent_info)
    final_rows, intent_info =  info.filter_info(rows, intent_info)
    return final_rows, intent_info

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
    filter("get movies of 2016" )
