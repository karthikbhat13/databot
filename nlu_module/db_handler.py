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
            row_tuple = tuple((row[1], row[2], row[4], row[5], row[6], row[8], row[9]))
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

def db_select(params):
    prefix = "SELECT * FROM movies WHERE "
    and_literal = " and "
    cols = params.keys()
    par = params.values()

    query_str = ''
    for col in cols:
        query_str += str(col)
        query_str += '='
        query_str += '?'
        query_str += and_literal
    
    query_str = query_str[:len(query_str)-len(and_literal)]
    print(query_str)

    print(tuple(par))

    con = db_connect()
    cur = con.cursor()

    fin_query = prefix+query_str
    print(fin_query)
    cur.execute(fin_query, tuple(par))

    rows = cur.fetchall()

    print(rows)

    return rows

if __name__ == "__main__":
    # print(populate_csv_db("imdb-alter.csv"))

    params = {'actor':'Tom Hanks'}
    db_select(params)