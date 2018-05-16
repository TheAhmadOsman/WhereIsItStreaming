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
    res = curs.execute("SELECT * FROM casts WHERE id = '%s'" %(movieId))
    castList = []
    for item in res:
        castDict = {}        
        castDict["id"] = item[0]
        castDict["character"] = item[1]
        castDict["name"] = item[2]
        castDict["profile_path"] = item[3]
        castList.append(castDict)
    return castList
    

def returnCrew(title):
    res = curs.execute("SELECT id FROM movies WHERE title = '%s'" %(title))
    movieId = None
    for item in res:
        movieId = item[0]
    if not movieId:
        return {}
    res = curs.execute("SELECT * FROM crews WHERE id = '%s'" %(movieId))
    crewList = []
    for item in res:
        crewDict = {}        
        crewDict["id"] = item[0]
        crewDict["name"] = item[1]
        crewDict["role"] = item[2]
        crewList.append(crewDict)
    return crewList

def returnRatings(title):
    res = curs.execute("SELECT id FROM movies WHERE title = '%s'" %(title))
    movieId = None
    for item in res:
        movieId = item[0]
    if not movieId:
        return {}
    res = curs.execute("SELECT * FROM ratings WHERE id = '%s'" %(movieId))
    ratingsList = []
    for item in res:
        ratingsDict = {}        
        ratingsDict["id"] = item[0]
        ratingsDict["rating"] = item[1]
        ratingsList.append(ratingsDict)
    return ratingsList
    
print(returnFilm("Cast Away"))
print(returnCast("Captain Phillips"))
print(returnCrew("The Da Vinci Code"))
print(returnRatings("Forrest Gump"))

db.close()
