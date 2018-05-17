import sqlite3


def returnFilm(title):
    db = sqlite3.connect("movies.db")
    curs = db.cursor()
    res = curs.execute(
        "SELECT * FROM movies WHERE title LIKE '{}%'".format(title))
    filmList = []
    for film in res:
        filmDict = {}
        filmDict["id"] = film[0]
        filmDict["IMDBid"] = film[1]
        filmDict["overview"] = film[2]
        filmDict["genres"] = film[3]
        filmDict["title"] = film[4]
        filmDict["release_date"] = film[5]
        filmDict["homepage"] = film[6]
        filmDict["poster_path"] = film[7]
        filmDict["tagline"] = film[8]
        filmList.append(filmDict)
    db.close()
    return filmList


def returnOneFilm(movieid):
    db = sqlite3.connect("movies.db")
    curs = db.cursor()
    res = curs.execute(
        "SELECT * FROM movies WHERE id = %d" % (movieid))
    filmList = []
    for film in res:
        filmDict = {}
        filmDict["id"] = film[0]
        filmDict["IMDBid"] = film[1]
        filmDict["overview"] = film[2]
        filmDict["genres"] = film[3]
        filmDict["title"] = film[4]
        filmDict["release_date"] = film[5]
        filmDict["homepage"] = film[6]
        filmDict["poster_path"] = film[7]
        filmDict["tagline"] = film[8]
        filmList.append(filmDict)
    db.close()
    return filmList


def returnCast(movieid):
    db = sqlite3.connect("movies.db")
    curs = db.cursor()
    res = curs.execute("""SELECT character, name, profile_path FROM movies INNER JOIN casts 
    ON movies.id = casts.id
    WHERE (movies.id = %d)""" % (movieid))
    castList = []
    for item in res:
        castDict = {}
        castDict["character"] = item[0]
        castDict["name"] = item[1]
        castDict["profile_path"] = item[2]
        castList.append(castDict)
    db.close()
    return castList


def returnCrew(movieid):
    db = sqlite3.connect("movies.db")
    curs = db.cursor()
    res = curs.execute("""SELECT name, role FROM movies INNER JOIN crews 
    ON movies.id = crews.id
    WHERE (movies.id = %d)""" % (movieid))
    crewList = []
    for item in res:
        crewDict = {}
        crewDict["name"] = item[0]
        crewDict["role"] = item[1]
        crewList.append(crewDict)
    db.close()
    return crewList


def returnRatings(movieid):
    db = sqlite3.connect("movies.db")
    curs = db.cursor()
    res = curs.execute("""SELECT AVG(rating) FROM movies INNER JOIN ratings 
    ON movies.id = ratings.id
    WHERE (movies.id = %d)
    GROUP BY ratings.id""" % (movieid))
    ratingsList = []
    for item in res:
        ratingsDict = {}
        ratingsDict["rating"] = round(item[0], 3)
        ratingsList.append(ratingsDict)
    db.close()
    return ratingsList


def insert(userid, movieid, table):
    db = sqlite3.connect("movies.db")
    curs = db.cursor()
    curs.execute("""INSERT INTO %s(movieid, userid) VALUES(?,?)""" %
                 (table), (movieid, userid))
    db.close()


def randomMovies():
    db = sqlite3.connect("movies.db")
    curs = db.cursor()
    res = curs.execute("""SELECT * FROM movies 
    WHERE id IN (SELECT id FROM movies ORDER BY RANDOM() LIMIT 50)""")
    filmList = []
    for film in res:
        if film[7] != "" and len(filmList) < 20:
            filmDict = {}
            filmDict["id"] = film[0]
            filmDict["IMDBid"] = film[1]
            filmDict["overview"] = film[2]
            filmDict["genres"] = film[3]
            filmDict["title"] = film[4]
            filmDict["release_date"] = film[5]
            filmDict["homepage"] = film[6]
            filmDict["poster_path"] = film[7]
            filmDict["tagline"] = film[8]
            filmList.append(filmDict)
    db.close()
    return filmList
