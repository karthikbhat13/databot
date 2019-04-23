import pandas as pd

import util
import db_handler

def filter_info(db_rows, intent_info):
    df = util.init_df()
    columns = df.columns

    col_ind = util.get_col_ind(columns)

    print(intent_info)
    rows_df = pd.DataFrame(data=db_rows[0], columns=columns)

    # print(rows_df)

    print(rows_df[intent_info['cols']])    
    # print(rows_df[['Title']])