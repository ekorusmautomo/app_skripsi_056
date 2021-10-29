import sqlite3 as lite
con=lite.connect("skripsiDB.db")
con.row_factory = lite.Row

cur = con.cursor()
cur.execute("SELECT * FROM dosen")

data = cur.fetchall()
res = cur.execute("SELECT * FROM dosen")
dat = cur.fetchall()
dosbim = dat[0][1]
print(dosbim)
