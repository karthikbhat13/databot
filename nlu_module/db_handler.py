import sqlite3
import os
import csv
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

def db_connect(path=DB_PATH):
    con = sqlite3.connect(path)
    return con

def db_create(con):
    drop_query = "DROP TABLE if exists movies"
    query = """
    create table movies (
        rank integer PRIMARY KEY,
        title text NOT NULL,
        genre text NOT NULL,
        director text NOT NULL,
        actor text NOT NULL,
        year integer NOT NULL,
        rating text NOT NULL,
        votes integer NOT NULL
    )"""

    con = db_connect()
    cur = con.cursor()
    cur.execute(drop_query)
    cur.execute(query)

def db_insert(con, rows):
    insert_query = """
        INSERT INTO movies (title, genre, director, actor, year, rating, votes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    cur = con.cursor()
    cur.executemany(insert_query, rows)
    
    return con.total_changes

def populate_csv_db(file_path):
    with open(file_path, 'r') as csv_file:
        csvreader = csv.reader(csv_file)

        list_tuple = []
        for row in csvreader:
            row_tuple = tuple((row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
            list_tuple.append(row_tuple)
    con = db_connect()
    db_create(con)
    try:
        lastrow = db_insert(con, list_tuple)
        con.commit()
        return lastrow
    except(Exception):
        print(sys.exc_info()[0])
        con.rollback()
    return False

def db_select(params, intent_info, col_type, adj_dic):
    space = ' '
    and_literal = " and "

    temp_col_type = {}
    for key, val in col_type.items():
        temp_col_type[key.lower()] = val
    col_type = temp_col_type
    prefix = "SELECT * FROM movies WHERE "
    for key, val in intent_info.items():
        if val:
            if key == 'get' or key == 'select':
                prefix = "SELECT * FROM movies WHERE "
            elif key == 'update':
                prefix = "UPDATE movies WHERE "
            elif key == 'delete':
                pre_type = 'DELETE FROM movies WHERE '
    

    cols = params.keys()
    
    query_str = ''
    for col in cols:
        query_str += str(col)
        if col_type[col] == 'string':
            query_str += ' LIKE '
        else:
            if col_type[col] == 'int' or col_type[col] == 'float':
                f = False
                for sym, b in adj_dic.items():
                    if b:
                        query_str += space+sym+space
                        f = True
                        break
                if not f:
                    query_str += '='

            else: 
                query_str += '='
        query_str += '?'
        query_str += and_literal
    
    query_str = query_str[:len(query_str)-len(and_literal)]
    print(query_str)


    con = db_connect()
    cur = con.cursor()

    par = []
    for key, val in params.items():
        if col_type[key] == 'string':
            par.append('%'+val+'%')
        else:
            par.append(val)

    print(tuple(par))

    fin_query = prefix+query_str
    print(fin_query)
    cur.execute(fin_query, tuple(par))

    rows = cur.fetchall()

    print(rows)

    return rows

if __name__ == "__main__":
    # print(populate_csv_db("imdb-alter.csv"))

    # params = {'actor':'Tom Hanks'}
    # db_select(params)

    populate_csv_db("imdb-alter.csv")