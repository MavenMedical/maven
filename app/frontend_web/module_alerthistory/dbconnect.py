import sqlalchemy.create_engine as ce

eng = ce('postgresql://maven:temporary@localhost/maven')
conn = eng.connect()
resultset = conn.execute('select * from terminology.concept where id=1000004')
for r in resultset:
    print(r)