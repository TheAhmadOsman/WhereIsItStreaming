import csv
import sqlite3
import json
from ast import literal_eval

# fetch the csv files from https://www.kaggle.com/rounakbanik/the-movies-dataset
# drop in a folder called kaggle and run, it should take around a minute or two

# setup movies.db
db = sqlite3.connect("movies.db")
curs = db.cursor()

# open our kaggle files
csvfile = open("kaggle/movies_metadata.csv", "r")
stars = open("kaggle/credits.csv", "r")
ratings = open("kaggle/ratings.csv", "r")

# initalize DictReader objects for the files
movieReader = csv.DictReader(csvfile)
starReader = csv.DictReader(stars)
ratingsReader = csv.DictReader(ratings)

# create empty tables
curs.execute("DROP TABLE IF EXISTS users")
curs.execute("CREATE TABLE IF NOT EXISTS users")
curs.execute("DROP TABLE IF EXISTS liked")
curs.execute("CREATE TABLE IF NOT EXISTS liked")
curs.execute("DROP TABLE IF EXISTS viewed")
curs.execute("CREATE TABLE IF NOT EXISTS viewed")
curs.execute("DROP TABLE IF EXISTS searched")
curs.execute("CREATE TABLE IF NOT EXISTS searched")

# create and populate movies table
print("Populating movies table")
curs.execute("DROP TABLE IF EXISTS movies")
curs.execute("CREATE TABLE IF NOT EXISTS movies(imdb_id TEXT, id TEXT UNIQUE, overview TEXT, genres TEXT, title TEXT, release_date TEXT, homepage TEXT, poster_path TEXT, tagline TEXT, PRIMARY KEY (imdb_id))")

# make genres look nice
for row in movieReader:
    genres = " - "
    genreDict = literal_eval(row["genres"])
    for item in genreDict:
        genres = genres + item["name"] + " - "

    curs.execute('''INSERT OR REPLACE INTO movies(imdb_id, id, overview, genres, title, release_date, homepage, poster_path, tagline) VALUES(?,?,?,?,?,?,?,?,?)''',
                 (row["imdb_id"], row["id"], row["overview"], genres, row["title"], row["release_date"], row["homepage"], row["poster_path"], row["tagline"]))
print("Movies table created successfully")

# create and populate both casts and crews tables
print("Populating casts and crews tables")
curs.execute("DROP TABLE IF EXISTS casts")
curs.execute("CREATE TABLE IF NOT EXISTS casts(id TEXT, character TEXT, name TEXT, profile_path TEXT, FOREIGN KEY (id) REFERENCES movies(id))")
curs.execute("DROP TABLE IF EXISTS crews")
curs.execute(
    "CREATE TABLE IF NOT EXISTS crews(id TEXT, name TEXT, role TEXT, FOREIGN KEY(id) REFERENCES movies(id))")

# choose select values
for row in starReader:
    cast = literal_eval(row["cast"])
    crew = literal_eval(row["crew"])
    for item in cast:
        if item["order"] < 7:
            curs.execute('''INSERT INTO casts(id, character, name, profile_path) VALUES(?,?,?,?)''',
                         (row["id"], item["character"], item["name"], item["profile_path"]))
    for item in crew:
        if item["department"] == "Directing" or item["department"] == "Writing":
            curs.execute('''INSERT INTO crews(id, name, role) VALUES(?,?,?)''',
                         (row["id"], item["name"], item["department"]))
print("Casts and crews created successfully")

# Turn plethora of ratings into a single average rating for each film
#ratingsDict = {}
# for row in ratingsReader:
#movieId = row["movieId"]
# if movieId not in ratingsDict:
#ratingsDict[movieId] = []
# ratingsDict[movieId].append(float(row["rating"]))
#avgRatings = []
# for idNum in ratingsDict:
#ratingSum = 0.0
#ratingLen = len(ratingsDict[idNum])
# for rating in ratingsDict[idNum]:
#ratingSum += rating
#avgRating = round((ratingSum / ratingLen), 2)
#avgRatings.append([idNum, avgRating, ratingLen])

# create and populate ratings table
print("Populating ratings tables")
curs.execute("DROP TABLE IF EXISTS ratings")
curs.execute(
    "CREATE TABLE IF NOT EXISTS ratings(id TEXT, rating TEXT, FOREIGN KEY(id) REFERENCES movies(id))")
for row in ratingsReader:
    curs.execute('''INSERT INTO ratings(id, rating) VALUES(?,?)''',
                 (row["movieId"], row["rating"]))
print("Ratings table created successfully")


# close up those files
csvfile.close()
stars.close()
ratings.close()

# commit and kill, lets get out of here
db.commit()
db.close()

print("Closing up shop..")
