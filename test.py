import records
db = records.Database('sqlite:///movies.db')
res = db.query("""select * from movies where id=862""")
print(res.first())
