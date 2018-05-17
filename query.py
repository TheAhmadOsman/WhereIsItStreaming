import sqlite3
db = sqlite3.connect("movies.db")
curs = db.cursor()


def returnFilm(title):
    res = curs.execute("SELECT * FROM movies WHERE title = '%s'" % (title))
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


def returnCast(movieid):
    res = curs.execute("""SELECT character, name, profile_path FROM movies INNER JOIN casts 
    ON movies.id = casts.id
    WHERE (movies.title = %d)""" % (movieid))
    castList = []
    for item in res:
        castDict = {}
        castDict["character"] = item[0]
        castDict["name"] = item[1]
        castDict["profile_path"] = item[2]
        castList.append(castDict)
    return castList


def returnCrew(movieid):
    res = curs.execute("""SELECT name, role FROM movies INNER JOIN crews 
    ON movies.id = crews.id
    WHERE (movies.id = %d)""" % (movieid))
    crewList = []
    for item in res:
        crewDict = {}
        crewDict["name"] = item[0]
        crewDict["role"] = item[1]
        crewList.append(crewDict)
    return crewList


def returnRatings(movieid):
    res = curs.execute("""SELECT AVG(rating) FROM movies INNER JOIN ratings 
    ON movies.id = ratings.id
    WHERE (movies.id = %d)
    GROUP BY ratings.id""" % (movieid))
    ratingsList = []
    for item in res:
        ratingsDict = {}
        ratingsDict["rating"] = round(item[0], 3)
        ratingsList.append(ratingsDict)
    return ratingsList


def insert(userid, movieid, table):
    curs.execute("""INSERT INTO %s(id, userid) VALUES(?,?)""" %
                 (table), (movieid, userid))


print(returnFilm("Forrest Gump"))
print(returnCast("Forrest Gump"))
print(returnCrew("Forrest Gump"))
print(returnRatings(862))
insert(999, 862, "searched")
res = curs.execute("SELECT * FROM searched")
for item in res:
    print(item)

db.close()
