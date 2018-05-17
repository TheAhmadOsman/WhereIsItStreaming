import csv
import sqlite3
import json
from ast import literal_eval

# fetch the csv files from https://www.kaggle.com/rounakbanik/the-movies-dataset
# drop in a folder called data and run, it should take around a minute or two

# setup movies.db
db = sqlite3.connect("movies.db")
curs = db.cursor()

# open our kaggle files
csvfile = open("data/movies_metadata.csv", "r")
stars = open("data/credits.csv", "r")
ratings = open("data/ratings.csv", "r")

# initalize DictReader objects for the files
movieReader = csv.DictReader(csvfile)
starReader = csv.DictReader(stars)
ratingsReader = csv.DictReader(ratings)

# create empty tables --> User-based
curs.execute(
    "CREATE TABLE IF NOT EXISTS users(userid INT UNIQUE, username CHAR(30) UNIQUE, email CHAR(64) UNIQUE, password CHAR(120), PRIMARY KEY(userid))")
curs.execute(
    "CREATE TABLE IF NOT EXISTS liked(id INT, userid INT, FOREIGN KEY(userid) REFERENCES users(userid), FOREIGN KEY(id) REFERENCES movies(id))")
curs.execute(
    "CREATE TABLE IF NOT EXISTS viewed(id INT, userid INT, FOREIGN KEY(userid) REFERENCES users(userid), FOREIGN KEY(id) REFERENCES movies(id))")
curs.execute(
    "CREATE TABLE IF NOT EXISTS searched(id INT, userid INT, FOREIGN KEY(userid) REFERENCES users(userid), FOREIGN KEY(id) REFERENCES movies(id))")

# create and populate movies table
print("Populating movies table")
curs.execute("CREATE TABLE IF NOT EXISTS movies(id int UNIQUE, imdb_id char(12), overview TEXT, genres TEXT, title TEXT, release_date TEXT, homepage TEXT, poster_path TEXT, tagline TEXT, PRIMARY KEY (id))")

# make genres look nice
for row in movieReader:
    genres = " - "
    genreDict = literal_eval(row["genres"])
    for item in genreDict:
        genres = genres + item["name"] + " - "
        try:
            curs.execute('''INSERT OR REPLACE INTO movies(id, imdb_id, overview, genres, title, release_date, homepage, poster_path, tagline) VALUES(?,?,?,?,?,?,?,?,?)''',
                         (int(row["id"]), row["imdb_id"], row["overview"], genres, row["title"], row["release_date"], row["homepage"], row["poster_path"], row["tagline"]))
        except Exception as e:
            continue

print("Movies table created successfully")

# create and populate both casts and crews tables
print("Populating casts and crews tables")
curs.execute("CREATE TABLE IF NOT EXISTS casts(id int, character TEXT, name TEXT, profile_path TEXT, FOREIGN KEY (id) REFERENCES movies(id))")
curs.execute(
    "CREATE TABLE IF NOT EXISTS crews(id int, name TEXT, role TEXT, FOREIGN KEY(id) REFERENCES movies(id))")

# choose select values
for row in starReader:
    cast = literal_eval(row["cast"])
    crew = literal_eval(row["crew"])
    for item in cast:
        if item["order"] < 7:
            curs.execute('''INSERT INTO casts(id, character, name, profile_path) VALUES(?,?,?,?)''',
                         (int(row["id"]), item["character"], item["name"], item["profile_path"]))
    for item in crew:
        if item["department"] == "Directing" or item["department"] == "Writing":
            curs.execute('''INSERT INTO crews(id, name, role) VALUES(?,?,?)''',
                         (int(row["id"]), item["name"], item["department"]))
print("Casts and crews created successfully")

# create and populate ratings table
print("Populating ratings tables")
curs.execute(
    "CREATE TABLE IF NOT EXISTS ratings(id int, rating float, FOREIGN KEY(id) REFERENCES movies(id))")
for row in ratingsReader:
    curs.execute('''INSERT INTO ratings(id, rating) VALUES(?,?)''',
                 (int(row["movieId"]), float(row["rating"])))
print("Ratings table created successfully")


# close up those files
csvfile.close()
stars.close()
ratings.close()

# commit and kill, lets get out of here
db.commit()
db.close()

print("Closing up shop..")
