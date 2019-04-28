import pandas as pd
from nltk import pos_tag, word_tokenize
import csv
import numpy
from textblob import TextBlob
from word2number import w2n
from nltk.corpus import wordnet

# def split_actors():
#     DATASET_PATH = "/home/karthik/databot/nlu_module/imdb-alter.csv"

#     with open(DATASET_PATH, 'r') as file:
#         csv_reader = csv.reader(file)

        

#         write_rows = []

#         for row in csv_reader:
#             temp_row = []
#             for i in range(len(row)):
#                 if i == 2:
#                     temp_row.append(row[i].split(',')[0])
#                 else:
#                     temp_row.append(row[i])
#             print(temp_row)
#             write_rows.append(temp_row)
    
#     with open("imdb-alter.csv", 'w') as write_file:
#         writer = csv.writer(write_file)

#         for row in write_rows:
#             writer.writerow(row)

def get_stats():
    DATASET_PATH = "/home/karthik/databot/nlu_module/imdb-alter.csv"

    df = pd.read_csv(DATASET_PATH)
    df.fillna(0)
    final_pos = {}
    count_pos = {}
    pos_count = {}

    for col in df.columns:        
    
        count_pos[col] = dict()
        count_pos[col]['proper'] = 0
        count_pos[col]['string'] = 0
        count_pos[col]['int'] = 0
        count_pos[col]['float'] = 0

        pos_count[col] = dict()

        for val in df[col].values:
            
            if isinstance(val, str):

                col_pos_list = TextBlob(val).tags

                nnp_list = list(filter(lambda pos : pos[1]=='NNP', col_pos_list))
                max_pos = max(list(map(lambda pos : pos[1], col_pos_list)))

                if max_pos not in pos_count[col].keys():
                    pos_count[col][max_pos] = 1
                else:
                    pos_count[col][max_pos] += 1

                if(len(nnp_list) == len(col_pos_list)):
                    count_pos[col]['proper'] += 1
                else:
                    count_pos[col]['string'] += 1
                    
                    
            elif isinstance(val, numpy.int64):
                if 'CD' in count_pos[col].keys():
                    pos_count[col]['CD'] += 1
                else:
                    pos_count[col]['CD'] = 1
                count_pos[col]['int'] += 1
                

            elif isinstance(val, numpy.float64):
                if 'CD' in count_pos[col].keys():
                    pos_count[col]['CD'] += 1
                else:
                    pos_count[col]['CD'] = 1
                count_pos[col]['float'] += 1
    return count_pos, pos_count            

def get_col_pos():
    count_type, count_pos = get_stats()
    final_type = {}
    final_pos = {}
    
    for key, count_arr in count_type.items():
        max = 0
        max_key = ''
        for t, count in count_arr.items():
            if count >= max:
                max_key = t
                max = count
        final_type[key] = max_key

    for key, count_arr in count_pos.items():
        max = 0
        max_key = ''
        for t, count in count_arr.items():
            if count >= max:
                max_key = t
                max = count
        final_pos[key] = max_key
    
    return final_type,final_pos


def get_number(text):
    tags = TextBlob(text).tags
    for tag in tags:
        if tag[1] == 'CD':
            if(tag[0].isdigit()):
                return int(tag[0])
            num = w2n.word_to_num(str(tag[0]))
            return num
    return False

def get_intent(text):
    text = text.lower()
    words = word_tokenize(text)

    intent_dic = {'select':False, 'delete':False, 'get':False, 'update': False}

    intent_syn = {'select':[], 'delete':[] ,'get':[], 'update': []}
    
    for intent in intent_dic.keys():
        for word in wordnet.synsets(intent):
            for lm in word.lemmas():
                intent_syn[intent].append(lm.name())
    print(intent_syn)
    any_true = False
    for word in words:
        for intent, syn in intent_syn.items():
            if word in syn:
                any_true = True
                intent_dic[intent] = True

    if not any_true:
        intent_dic['get'] = True    
    return intent_dic

def get_col_ind(columns):
    columns_ind = {}

    for ind in range(0, len(columns)):
        columns_ind[columns[ind]] = ind+1
    return columns_ind

def init_df(path='/home/karthik/databot/nlu_module/imdb-alter.csv'):
    return pd.read_csv(path)

def adj_syn():

    adj_high = ['greater', 'higher', 'more', 'better', 'after']
    high_syn = []
    for word in adj_high:
        for syn in wordnet.synsets(word):
            for lem in syn.lemmas():
                high_syn.append(lem.name())

    adj_low = ['less', 'lower', 'before', 'low', 'better']
    low_syn = []
    for word in adj_low:
        for syn in wordnet.synsets(word):
            for lem in syn.lemmas():
                low_syn.append(lem.name())

    return high_syn, low_syn

def get_adj(text):
    tags = TextBlob(text).tags

    adj_dic = {'>=':False, '<=':False}

    high_syn, low_syn = adj_syn()

    tag = filter(lambda pos : pos[1] == 'JJR', tags)

    for t in tag:
        if t[0] in high_syn:
            adj_dic['>='] = True
        elif t[0] in low_syn:
            adj_dic['<='] = True
    
    return adj_dic

if __name__ == "__main__":
    # print(get_col_pos())
    # print(get_intent('can I have three movies'))
    print(get_number('select four movies'))
    # print(split_actors())
    # print(get_adj('rating higher than 9'))