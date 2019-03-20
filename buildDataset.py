import requests
import json
import psycopg2
import concurrent.futures
import time
from csv import DictReader

API_KEY = "2c95af987a6c080a7a90af7109e06abb"
FILE_PATH = "data/ml-latest/links.csv"
THREADS = 1

#Use with caution! This will delete the current table if set to True
NEW_TABLE = False

COLUMN_NAMES = ["adult", "backdrop_path", "belongs_to_collection", "budget", "genres",
                "homepage", "id", "imdb_id", "original_language", "original_title",
                "overview", "popularity", "poster_path", "production_companies",
                "production_countries", "release_date", "revenue", "runtime", "spoken_languages",
                "status", "tagline", "title", "video", "vote_average", "vote_count"]

conn = psycopg2.connect(database = "movies", user = "postgres",
                        password = "howdy", host = "127.0.0.1", port="5432")
        
def retrieve(url):
    cur = conn.cursor()
    
    cur.execute('''CREATE TABLE IF NOT EXISTS "movies"(
              adult BOOLEAN,
              backdrop_path TEXT,
              belongs_to_collection TEXT,
              budget TEXT,
              genres TEXT [],
              homepage TEXT,
              id INT PRIMARY KEY ,
              imdb_id TEXT,
              original_language TEXT,
              original_title TEXT,
              overview TEXT,
              popularity FLOAT,
              poster_path TEXT,
              production_companies TEXT [],
              production_countries TEXT [],
              release_date TEXT,
              revenue INT,
              runtime INT,
              spoken_languages TEXT [],
              status TEXT,
              tagline TEXT,
              title TEXT,
              video BOOLEAN,
              vote_average FLOAT,
              vote_count INT,
              error BOOLEAN,
              error_code TEXT
            );''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS "credits"(
              filmCast TEXT [],
              filmCrew TEXT [],
              id INT PRIMARY KEY,
              error BOOLEAN,
              error_code TEXT
            );''')    
    
    response = requests.get(url)
    if response.status_code != 200:
        cur.close()
        raise Exception(f"response code {response.status_code}")
    resDict = json.loads(response.content)
    valueList = []
    for col in COLUMN_NAMES:
        try:
            if resDict[col] == "":
                valueList.append(None)
            else:
                if type(resDict[col]) == type({}):
                    valueList.append(json.dumps(resDict[col]))
                elif type(resDict[col]) == type([]):
                    stringifyList = []
                    for item in resDict[col]:
                        stringifyList.append(json.dumps(item))
                    valueList.append(stringifyList)
                else:
                    valueList.append(resDict[col])
        except:
            valueList.append(None)
            
    #error = False, error_code = None
    valueList.append(False)
    valueList.append(None)
    
    strings = "("
    
    for i in range(len(valueList)):
        strings = strings + "%s, "
    strings = strings[:len(strings) - 2] + ")"
    try:
        cur.execute(f'''INSERT INTO movies
        VALUES {strings}''', valueList)
    except psycopg2.IntegrityError:
        cur.close()
        print(f"id {valueList[6]} has already been assigned")
        return
        
    #onto credits
    
    valueList = []
    stringifyList = []
    for item in resDict["credits"]["cast"]:
        stringifyList.append(json.dumps(item))
    valueList.append(stringifyList)
    
    stringifyList = []
    for item in resDict["credits"]["crew"]:
        stringifyList.append(json.dumps(item))
    valueList.append(stringifyList)
    
    valueList.append(resDict["id"])
    
    #error = False, error_code = None
    valueList.append(False)
    valueList.append(None)
    
    strings = "("
    
    for i in range(len(valueList)):
        strings = strings + "%s, "
    strings = strings[:len(strings) - 2] + ")"    
    
    try:
        cur.execute(f'''INSERT INTO credits
        VALUES {strings}''', valueList)
    except psycopg2.IntegrityError:
        cur.close()
        print(f"id {valueList[6]} has already been assigned")
        return
    
    cur.close()
    
                        

def getURLs():
    urls = []
    with open(FILE_PATH) as f:
        for row in DictReader(f):
            tmdbId = row["tmdbId"]
            if not tmdbId:
                continue
            urls.append(f"https://api.themoviedb.org/3/movie/{tmdbId}?api_key={API_KEY}&language=en-US&external_source=imdb_id&append_to_response=credits")
    return urls

def main():
    cur = conn.cursor()
    
    if NEW_TABLE == True:
        cur.execute("DROP TABLE IF EXISTS movies")  
        cur.execute("DROP TABLE IF EXISTS credits")
        
    done = 0
    errors = 0    
    
    urls = getURLs()[:150]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers = THREADS) as executor:
        time1 = time.time()
        future_to_url = {executor.submit(
                retrieve, url): url for url in urls}
        
        for future in concurrent.futures.as_completed(future_to_url):
            row = future_to_url[future]
                        
            try:
                future.result()
                done += 1
            except ValueError:
                continue
            except Exception as exc:
                print(f"Error: {exc}")
                errors += 1
                idBegin = row.find("/movie")
                idEnd = row.find("?")
                try:
                    errId = int(row[idBegin + 7:idEnd])
                except:
                    print("Invalid id, skipping entry")
                    continue
                try:
                    cur.execute('''INSERT INTO movies (id, error, error_code)
                    VALUES (%s, %s, %s)''', [errId, True, str(exc)])
                except psycopg2.IntegrityError:
                    print(f"id {errId} has already been assigned")
                    conn.rollback()
                    
                try:
                    cur.execute('''INSERT INTO credits (id, error, error_code)
                    VALUES (%s, %s, %s)''', [errId, True, str(exc)]) 
                except psycopg2.IntegrityError:
                    print(f"id {errId} has already been assigned")
                    conn.rollback()
                    
            if done % THREADS == 0:
                print(f"{done} entries logged")
                print(f"{errors} errors encountered")
            conn.commit()
            
        time2 = time.time()
        
        completedTime = time2 - time1
        
        completedTime = round(completedTime)
        
        
    cur.execute("SELECT COUNT(*) FROM movies")
    filmCount = cur.fetchall()[0][0]
    
    cur.execute("SELECT COUNT(*) FROM credits")
    creditCount = cur.fetchall()[0][0]
    
    print(f"Database size: {filmCount} films and {creditCount} credits")
    print(f"Runtime: {completedTime} seconds")
    
    cur.close()
    conn.close()
    
if __name__ == "__main__":
    main()