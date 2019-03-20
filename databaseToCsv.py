import sys
import psycopg2

conn = psycopg2.connect(database = "movies", user = "postgres",
                        password = "howdy", host = "127.0.0.1", port="5432")

movieQuery = "SELECT * FROM movies"
cur = conn.cursor()
outputMovieQuery = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(movieQuery)

with open('data/movies.csv', 'w') as f:
    cur.copy_expert(outputMovieQuery, f)
    
creditQuery = "SELECT * FROM credits"
cur = conn.cursor()
outputCreditQuery = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(creditQuery)

with open('data/credits.csv', 'w') as f:
    cur.copy_expert(outputCreditQuery, f)

conn.close()