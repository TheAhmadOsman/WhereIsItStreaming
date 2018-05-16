import csv
import sqlite3
import json
#fetch the csv files from https://www.kaggle.com/rounakbanik/the-movies-dataset
#drop in a folder called kaggle and run, it should take less than 5 seconds

db = sqlite3.connect("movies.db")
curs = db.cursor()
curs.execute("DROP TABLE IF EXISTS movies")
curs.execute("CREATE TABLE movies(imdb_id TEXT, id TEXT UNIQUE, genres TEXT, title TEXT, release_date TEXT, homepage TEXT, poster_path TEXT, tagline TEXT, PRIMARY KEY (imdb_id))")
csvfile = open("kaggle/movies_metadata.csv", "r")
stars = open("kaggle/credits.csv", "r")
movieReader = csv.DictReader(csvfile)
starReader = csv.DictReader(stars)
for row in movieReader:
    curs.execute('''INSERT OR REPLACE INTO movies(imdb_id, id, genres, title, release_date, homepage, poster_path, tagline) VALUES(?,?,?,?,?,?,?,?)''', (row["imdb_id"], row["id"], row["genres"], row["title"], row["release_date"], row["homepage"], row["poster_path"], row["tagline"]))

curs.execute("DROP TABLE IF EXISTS casts")
curs.execute("CREATE TABLE IF NOT EXISTS casts(id TEXT, cast TEXT, crew TEXT, PRIMARY KEY(id), FOREIGN KEY (id) REFERENCES movies(id))")
key = 0
for row in starReader:
    curs.execute('''INSERT OR REPLACE INTO casts(id, cast, crew) VALUES(?,?,?)''', (row["id"], row["cast"], row["crew"]))
    
csvfile.close()
stars.close()

db.commit()
db.close()
