import db_handler
import pandas as pd
from fuzzywuzzy import fuzz, process
import util

def retry(col, text):
    df = util.init_df("/home/karthik/databot/nlu_module/imdb-alter.csv")

    columns = df.columns

    util.get_col_ind(columns)
    
    col_rows = df[[col]]

    matches = get_match(col_rows, text)

    print(matches)
    rows = []
    for match in matches:
        row = df.iloc[match[0]]
        print(row)
        rows.append(row)
    return rows

def get_match(col_rows, text):
    col_rows_values = [e[0] for e in col_rows.values]

    matches = process.extractBests(text, col_rows_values, score_cutoff=70)
    print(matches)
    
    ind_match = []
    ind = -1
    for match in matches:
        ind = col_rows_values.index(match[0], ind+1)
        ind_match.append((ind, match[0]))
    return ind_match
    
if __name__ == "__main__":
    retry('Actor', 'acted by Tom Hanks')