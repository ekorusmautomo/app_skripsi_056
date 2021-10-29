import sqlite3 as lite
nik = '056'
password = '05'
con=lite.connect('skripsiDB.db')
cur=con.cursor()
cur.execute("SELECT COUNT(1) FROM users WHERE nik = (?)", [nik])
if cur.fetchone()[0]:
    cur.execute("SELECT password, level FROM users WHERE nik =(?)", [nik])
    for row in cur.fetchall():
        if password == row[0]:
            print('berhasil login')
        else:
            print('salah password')
    else:
        print('salah nik')
print('cek')
