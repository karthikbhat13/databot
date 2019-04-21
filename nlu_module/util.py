import pandas as pd
from nltk import pos_tag
import csv
import numpy
from textblob import TextBlob
# def split_actors():
    # DATASET_PATH = "/home/karthik/databot/nlu_module/IMDB-Movie-Data.csv"

#     with open(DATASET_PATH, 'r') as file:
#         csv_reader = csv.reader(file)

        

#         write_rows = []

#         for row in csv_reader:
#             temp_row = []
#             for i in range(len(row)):
#                 if i == 5:
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

def get_col_pos(count_type, count_pos):
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

count_type, count_pos = get_stats()
print(get_col_pos(count_type, count_pos))