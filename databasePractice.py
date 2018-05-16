import sqlite3
db = sqlite3.connect("movies.db")
curs = db.cursor()

def returnFilm(title):
    res = curs.execute("SELECT * FROM movies WHERE title = '%s'" %(title))
    film = None
    filmDict = {}
    for item in res:
        film = item
    if not film:
        return filmDict
    filmDict["IMDBid"] = film[0]
    filmDict["id"] = film[1]
    filmDict["overview"] = film[2]
    filmDict["genres"] = film[3]
    filmDict["title"] = film[4]
    filmDict["release_date"] = film[5]
    filmDict["homepage"] = film[6]
    filmDict["poster_path"] = film[7]
    filmDict["tagline"] = film[8]
    return filmDict

def returnCast(title):
    res = curs.execute("SELECT id FROM movies WHERE title = '%s'" %(title))
    movieId = None
    for item in res:
        movieId = item[0]
    if not movieId:
        return {}
    res = curs.execute("SELECT * FROM cast WHERE id = '%s'" %(

def returnCrew(title):
    res = curs.execute("SELECT id FROM movies WHERE title = '%s'" %(title))
    movieId = None
    for item in res:
        movieId = item[0]
    if not movieId:
        return {}

def returnReviews(title):
    res = curs.execute("SELECT id FROM movies WHERE title = '%s'" %(title))
    movieId = None
    for item in res:
        movieId = item[0]
    if not movieId:
        return {}

returnCast("Cast Away")

db.close()
