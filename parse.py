import csv
import sqlite3
import json

#fetch the csv files from https://www.kaggle.com/rounakbanik/the-movies-dataset
#drop in a folder called kaggle and run, it should take less than a minute

#setup movies.db
db = sqlite3.connect("movies.db")
curs = db.cursor()

#open our kaggle files
csvfile = open("kaggle/movies_metadata.csv", "r")
stars = open("kaggle/credits.csv", "r")
ratings = open("kaggle/ratings.csv", "r")

#initalize DictReader objects for the files
movieReader = csv.DictReader(csvfile)
starReader = csv.DictReader(stars)
ratingsReader = csv.DictReader(ratings)

#create and populate movies table
curs.execute("DROP TABLE IF EXISTS movies")
curs.execute("CREATE TABLE IF NOT EXISTS movies(imdb_id TEXT, id TEXT UNIQUE, genres TEXT, title TEXT, release_date TEXT, homepage TEXT, poster_path TEXT, tagline TEXT, PRIMARY KEY (imdb_id))")
for row in movieReader:
    curs.execute('''INSERT OR REPLACE INTO movies(imdb_id, id, genres, title, release_date, homepage, poster_path, tagline) VALUES(?,?,?,?,?,?,?,?)''', (row["imdb_id"], row["id"], row["genres"], row["title"], row["release_date"], row["homepage"], row["poster_path"], row["tagline"]))

#create and populate casts table
curs.execute("DROP TABLE IF EXISTS casts")
curs.execute("CREATE TABLE IF NOT EXISTS casts(id TEXT UNIQUE, cast TEXT, crew TEXT, PRIMARY KEY(id), FOREIGN KEY (id) REFERENCES movies(id))")
for row in starReader:
    curs.execute('''INSERT OR REPLACE INTO casts(id, cast, crew) VALUES(?,?,?)''', (row["id"], row["cast"], row["crew"]))


#Turn plethora of ratings into a single average rating for each film
ratingsDict = {}
for row in ratingsReader:
    movieId = row["movieId"]
    if movieId not in ratingsDict:
        ratingsDict[movieId] = []
    ratingsDict[movieId].append(float(row["rating"]))
avgRatings = []
for idNum in ratingsDict:
    ratingSum = 0.0
    ratingLen = len(ratingsDict[idNum])
    for rating in ratingsDict[idNum]:
        ratingSum += rating
    avgRating = round((ratingSum / ratingLen), 2)
    avgRatings.append([idNum, avgRating, ratingLen])

#create and populate ratings table
curs.execute("DROP TABLE IF EXISTS ratings")
curs.execute("CREATE TABLE IF NOT EXISTS ratings(id TEXT UNIQUE, rating TEXT, ratingCount TEXT, PRIMARY KEY(id), FOREIGN KEY(id) REFERENCES movies(id))")
for item in avgRatings:
    curs.execute('''INSERT OR REPLACE INTO ratings(id, rating, ratingCount) VALUES(?,?,?)''', (item[0], item[1], item[2]))


#close up those files
csvfile.close()
stars.close()
ratings.close()

#commit and kill, lets get out of here
db.commit()
db.close()
