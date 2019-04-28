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
    print(col_rows_values)
    matches = process.extractBests(text, col_rows_values, score_cutoff=70)
    print(matches)
    
    ind_match = []
    ind = -1
    for match in matches:
        try:
            ind = col_rows_values.index(match[0], ind+1)
            ind_match.append((ind, match[0]))
        except:
            continue
    return ind_match

def no_col_match(text):
    df = util.init_df("/home/karthik/databot/nlu_module/imdb-alter.csv")

    columns = df.columns

    for col in columns:
        rows = retry(col, text)
        if len(rows) > 0:
            return rows
    return False
if __name__ == "__main__":
    retry('Actor', 'acted by Tom Hanks')