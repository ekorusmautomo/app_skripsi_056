import sqlite3 as lite
con=lite.connect("skripsiDB.db")
con.row_factory = lite.Row
cur = con.cursor()
nik = '5'
cur.execute("select * from users where nik=(?)", [nik])
user = cur.fetchall()
username = user[0][2]
name = user[0][0]
print(name)
print(username)

cur.execute("select * from dosen")
rows = cur.fetchall()
print(rows)
con.close()
