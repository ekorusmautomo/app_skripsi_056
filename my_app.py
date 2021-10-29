from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, jsonify
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
#from passlib.hash import sha256_crypt
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os
import json
import sqlite3 as lite
from peewee import *
import time, socket
import netifaces as ni
from flask_restful import Resource, Api, reqparse

UPLOAD_FOLDER = 'static/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
api = Api(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

con = lite.connect('skripsiDB.db')
cur = con.cursor()


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
	if 'nik' in session:
		nik_session = session['nik']
		if session['levelakses']=="1":
			# pengguna ="mahasiswa"
			return redirect(url_for('dashboard_mahasiswa', session_nik=nik_session, levelakses=session['levelakses']))
		elif session['levelakses']=="2":
			# pengguna ="dosen"
			return redirect(url_for('dashboard_dosbim', session_nik=nik_session, levelakses=session['levelakses']))
		else:
			#return render_template('dashboard_admin.html', session_nik=nik_session, levelakses=session['levelakses'])
			return redirect(url_for('dashboard_admin', session_nik=nik_session, levelakses=session['levelakses']))
	else:
		return render_template('index.html')


@app.route('/logout')
def logout():
    savelogout()
    session.pop('nik', None)
    session.pop('levelakses', None)
    return redirect(url_for('index'))


@app.route('/showLogin')
def showLogin():
    return render_template("login.html")


#login multi user
@app.route('/goLogin', methods=['GET','POST'])
def goLogin():
	error = ''
	level_akses_session = ""
	if request.method == 'POST':
		nik_form = request.form['nik']
		password_form = request.form['password']

		con=lite.connect('skripsiDB.db')
		cur=con.cursor()
		cur.execute("SELECT COUNT(1) FROM users WHERE nik = (?)", [nik_form])
		if cur.fetchone()[0]:
			cur.execute("SELECT password, level FROM users WHERE nik =(?)", [nik_form])
			for row in cur.fetchall():
				if password_form == row[0]:
					session['nik'] = nik_form
					session['levelakses'] = row[1]
					savelogin()
					flash('You were successfully logged in')
					return redirect(url_for('index'))
				else:
					error = 'Invalid Credential - Error Password'
					#return render_template('salahpassword.html')
			else:
				error = 'Invalid Credential - Error Username!!!'
	return render_template('login.html', error=error)


def savelogin():
	ni.ifaddresses('wlp3s0')
	ip = ni.ifaddresses('wlp3s0')[2][0]['addr']
	nik = request.form['nik']
	now = time.time()
	saiki = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))
	level = session['levelakses']
	type = 'login'
	con = lite.connect('skripsiDB.db')
	con.row_factory = lite.Row
	with con:
		cur=con.cursor()
		cur.execute("INSERT INTO login (nik,ip,time,level,type) Values (?,?,?,?,?)", (nik,ip,saiki,level,type))
		con.commit()
		cur.close()


def savelogout():
	ni.ifaddresses('wlp3s0')
	ip = ni.ifaddresses('wlp3s0')[2][0]['addr']
	nik = session['nik']
	now = time.time()
	saiki = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))
	level = session['levelakses']
	type = 'logout'
	con = lite.connect('skripsiDB.db')
	con.row_factory = lite.Row
	with con:
		cur=con.cursor()
		cur.execute("INSERT INTO login (nik,ip,time,level,type) Values (?,?,?,?,?)", (nik,ip,saiki,level,type))
		con.commit()
		cur.close()	


@app.route('/showregister')
def showregister():
	return render_template("register.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		name = request.form['name']
		nik = request.form['nik']
		username = request.form['username']
		password = request.form['password']
		level = '1'
		con = lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		with con:
			cur = con.cursor()
			cur.execute("INSERT INTO users (name, nik, username, password, level) VALUES (?,?,?,?,?)", (name, nik, username, password, level))
			con.commit()
			cur.close()
			return redirect(url_for('showLogin'))


# admin area
@app.route('/dashboard_admin')
def dashboard_admin():
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("select * from dosen")
	rows = cur.fetchall()
	
	cur.execute("select * from users where nik=(?)", [nik_session])
	user = cur.fetchall()
	namauser = user[0][2]
	return render_template("dashboard_admin.html", rows = rows, session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser)


# add data dosen
@app.route('/add_data_dosen', methods=['GET', 'POST'])
def add_data_dosen():
   if request.method == 'POST':
      nik_dosen = request.form['nik_dosen']
      dosbim = request.form['dosbim']
      alamat = request.form['alamat']
      telp = request.form['telp']
      fakultas = request.form['fakultas']
      email_dosbim = request.form['email_dosbim']
      pend_terakhir = request.form['pend_terakhir']
      prodi = request.form['prodi']
      bid_ilmu = request.form['bid_ilmu']
      spesialisasi = request.form['spesialisasi']
      bhs_program = request.form['bhs_program']

      # create cursor
      con=lite.connect("skripsiDB.db")
      con.row_factory = lite.Row

      cur = con.cursor()
      cur.execute("INSERT INTO dosen (nik_dosen,dosbim,alamat,telp,fakultas,email_dosbim,pend_terakhir,prodi,bid_ilmu,spesialisasi,bhs_program) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (nik_dosen, dosbim, alamat, telp, fakultas, email_dosbim, pend_terakhir, prodi, bid_ilmu, spesialisasi, bhs_program))
      # commit to DB
      con.commit()

      # close connection
      cur.close()

      flash(' Data Dosen Berhasil di Tambahkan', 'success')

      return redirect(url_for('dashboard_admin'))
   return render_template('add_data_dosen.html')


@app.route('/showuserlist')
def showuserlist():
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("select * from users")
	rows = cur.fetchall()

	cur.execute("select * from users where nik=(?)", [nik_session])
	user = cur.fetchall()
	namauser = user[0][2]
	return render_template("userlist.html", rows = rows, session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser)


@app.route('/show_update_userlist/<string:record_id>')
def show_update_userlist(record_id):
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("select * from users where nik=(?)", [record_id])
	rows = cur.fetchall()

	cur.execute("select * from users where nik=(?)", [nik_session])
	user = cur.fetchall()
	namauser = user[0][2]
	return render_template("edit_user.html", rows = rows, session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser)


@app.route('/update_userlist/<string:record_id>', methods=['GET', 'POST'])
def update_userlist(record_id):
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("select * from users where nik=(?)", [nik_session])
	user = cur.fetchall()
	namauser = user[0][2]

	if request.method == 'POST':
		level_form = request.form['level']
		con=lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute("UPDATE users SET level=? WHERE nik = ?", (level_form, record_id))
		con.commit()
		cur.close()

		return redirect(url_for('showuserlist'))
	return render_template('edit_user.html',session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser)



# area mahasiswa
@app.route('/dashboard_mahasiswa')
def dashboard_mahasiswa():
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("select * from users where nik=(?)", [nik_session])
	user = cur.fetchall()
	namauser = user[0][2]
	return render_template('dashboard_mahasiswa.html', session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser)


@app.route('/add_pengajuan', methods=['GET', 'POST'])
def add_pengajuan():
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row

	cur = con.cursor()
	cur.execute("SELECT * FROM dosen")

	data = cur.fetchall()

	if request.method == 'POST':
		judul = request.form['judul']
		nik_dosen = request.form['dosbim']
		file = request.files['file']
		sinopsis = request.form['sinopsis']

		res = cur.execute("SELECT * FROM dosen where nik_dosen=(?)",[nik_dosen])
		dat = cur.fetchall()
		dosbim = dat[0][1]
		print(dat)
		print(nik_dosen)

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

		con=lite.connect("skripsiDB.db")
		con.row_factory = lite.Row

		cur = con.cursor()
		cur.execute("INSERT INTO pengajuan (nik,judul,nik_dosen,dosbim,file,sinopsis,status) VALUES (?,?,?,?,?,?,?)",
                  (session['nik'],judul, nik_dosen, dosbim, filename, sinopsis, 'Menunggu Konfirmasi Dosen'))

		con.commit()
		cur.close()

		return redirect(url_for('dashboard_mahasiswa'))
	return render_template('add_pengajuan.html', data=data)


@app.route('/edit_pengajuan', methods=['GET', 'POST'])
#@is_logged_in
def edit_pengajuan():
	nik_session = session['nik']
	# create cursor
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row

	cur = con.cursor()
	cur.execute("SELECT * FROM dosen")

	dt_dosen = cur.fetchall()
	cur.execute("select * from users where nik=(?)", [nik_session])
	user = cur.fetchall()
	namauser = user[0][2]
	# get article by id
	nik = session['nik']
	result = cur.execute("SELECT * FROM pengajuan WHERE nik = (?)", [nik])
	data = cur.fetchall()

	if request.method == 'POST':

		nik_session = session['nik']

		nik_dosen = request.form['dosbim']
		judul = request.form['judul']
		sinopsis = request.form['sinopsis']

		res = cur.execute("SELECT * FROM dosen where nik_dosen=(?)",[nik_dosen])
		dat = cur.fetchall()
		dosbim = dat[0][1]
		print(nik_dosen)

		con=lite.connect("skripsiDB.db")
		con.row_factory = lite.Row

		cur = con.cursor()

		# execute
		cur.execute("UPDATE pengajuan SET nik_dosen=?, judul=?, dosbim=?, sinopsis=? WHERE nik = ?", (nik_dosen, judul, dosbim, sinopsis, nik))
		con.commit()
		cur.close()

		flash('Update Berhasil', 'success')

		return redirect(url_for('status'))
	return render_template('edit_pengajuan.html', dt_dosen=dt_dosen,session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser)


@app.route('/delete_pengajuan', methods=['POST'])
def delete_pengajuan():
	if request.method == 'POST':
		nik_session = session['nik']

		con = lite.connect('skripsiDB.db')
		cur = con.cursor()

		cur.execute("DELETE FROM pengajuan WHERE nik=(?)",[nik])
		cur.execute("select * from users where nik=(?)", [nik_session])
		user = cur.fetchall()
		namauser = user[0][2]
		con.commit()
	return redirect(url_for('status'), session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser)


@app.route('/detail_pengajuan')
def detail_pengajuan():
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("SELECT * FROM pengajuan WHERE nik = (?)", [nik_session])
	data = cur.fetchall()
	cur.execute("select * from users where nik=(?)", [nik_session])
	user = cur.fetchall()
	namauser = user[0][2]

	con.close()
	return render_template("delete_pengajuan.html", data = data,session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser)


@app.route('/status')
def status():
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("SELECT * FROM pengajuan WHERE nik=(?)", [nik_session])
	data = cur.fetchall()

	cur.execute("select * from users where nik=(?)", [nik_session])
	user = cur.fetchall()
	namauser = user[0][2]
	return render_template('status.html', data=data,session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser)


@app.route('/bimbingan')
def bimbingan():
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("SELECT * FROM pengajuan WHERE nik=(?)", [nik_session])
	data = cur.fetchall()

	cur.execute("select * from users where nik=(?)", [nik_session])
	user = cur.fetchall()
	namauser = user[0][2]
	return render_template("bimbingan.html", data=data,session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser)


@app.route('/add_bimbingan', methods=['GET', 'POST'])
def add_bimbingan():
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("SELECT * FROM pengajuan WHERE nik=(?)", [nik_session])
	data = cur.fetchall()
	dt_nikdosen = data[0][2]
	dt_namadosen = data[0][3]
	if request.method == 'POST':
		catatan_form = request.form['catatan']
		file = request.files['file']

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

		con=lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute("INSERT INTO bimbingan (nik, nik_dosen, dosbim, catatan, file) VALUES (?,?,?,?,?)", (nik_session, dt_nikdosen, dt_namadosen, catatan_form,filename))
		con.commit()
		cur.close()

		return redirect(url_for('status'))
	return render_template('bimbingan.html',data=data)


# dosbim area
@app.route('/dashboard_dosbim')
def dashboard_dosbim():
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("SELECT * FROM pengajuan WHERE nik_dosen = (?)", [nik_session])
	data = cur.fetchall()

	cur.execute("select * from users where nik=(?)", [nik_session])
	user = cur.fetchall()
	namauser = user[0][2]
	con.close()
	return render_template("dashboard_dosbim.html", data = data, session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser)


@app.route('/approve/<string:record_id>', methods=['GET', 'POST'])
def approve(record_id):
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	status = 'Pangajuan diterima'
	cur.execute("UPDATE pengajuan SET status=? WHERE nik=?", (status, record_id))
	con.commit()
	cur.close()
	return redirect(url_for('dashboard_dosbim'))


@app.route('/decline/<string:record_id>', methods=['GET', 'POST'])
def decline(record_id):
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	status = 'Pangajuan ditolak'
	cur.execute("UPDATE pengajuan SET status=? WHERE nik=?", (status, record_id))
	con.commit()
	cur.close()
	return redirect(url_for('dashboard_dosbim'))


@app.route('/showformbimbingan/<string:record_id>')
def showformbimbingan(record_id):
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("SELECT * FROM bimbingan WHERE nik=(?)", [record_id])
	data = cur.fetchall()

	curr = con.cursor()
	curr.execute("SELECT * FROM pengajuan WHERE nik=(?)", [record_id])
	dt = curr.fetchall()
	dt_judul = dt[0][1]
	dt_sinopsis = dt[0][5]


	cur.execute("select * from users where nik=(?)", [nik_session])
	user = cur.fetchall()
	namauser = user[0][2]
	return render_template("bimbingandosen.html", data = data, session_nik=nik_session, levelakses=session['levelakses'], namauser=namauser, dt=dt)


@app.route('/add_bimbingandosen/<string:record_id>', methods=['GET', 'POST'])
def add_bimbingandosen(record_id):
	#record_id berisi NIM mahasiswa
	nik_session = session['nik']
	con=lite.connect("skripsiDB.db")
	con.row_factory = lite.Row
	cur = con.cursor()
	cur.execute("SELECT * FROM pengajuan WHERE nik_dosen=(?)", [nik_session])
	data = cur.fetchall()
	dt_namadosen = data[0][3]
	if request.method == 'POST':
		catatan_form = request.form['catatan']
		con=lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute("INSERT INTO bimbingan (nik, nik_dosen, dosbim, catatan) VALUES (?,?,?,?)", (record_id, nik_session,dt_namadosen, catatan_form))
		con.commit()
		cur.close()

		return redirect(url_for('dashboard_dosbim'))
	return render_template('bimbingandosen.html',data=data,session_nik=nik_session, levelakses=session['levelakses'])


# BAGIAN WEB SERVICE
class userWS(Resource):
	def get(self):
		parserWS = reqparse.RequestParser()
		parserWS.add_argument('dataNik')

		argsWS = parserWS.parse_args()

		user_dataid = argsWS.get('dataNik')

		con = lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		with con:
			cur = con.cursor()
			if user_dataid:
				cur.execute("select * from users where nik=(?)",[user_dataid])
				data = [{
				'Name':row[0],
				'NIK':row[1],
				'Username':row[2],
				'Password':row[3],
				'Level' :row[4]
				}for row in cur.fetchall()]
				con.commit()
				cur.close()
			else:
				cur.execute("select * from users")
				data = [{
				'Name':row[0],
				'NIK':row[1],
				'Username':row[2],
				'Password':row[3],
				'Level' :row[4]
				}for row in cur.fetchall()]
				con.commit()
				cur.close()	
		return jsonify(data)

	def post(self):
		parserWS = reqparse.RequestParser()
		parserWS.add_argument('dataNik')
		parserWS.add_argument('dataName')
		parserWS.add_argument('dataUsername')
		parserWS.add_argument('dataPassword')
		parserWS.add_argument('dataLevel')

		argsWS = parserWS.parse_args()

		user_dataid = argsWS.get('dataNik')
		user_dataname = argsWS.get('dataName')
		user_datausername = argsWS.get('dataUsername')
		user_datapassword = argsWS.get('dataPassword')
		user_datalevel = argsWS.get('dataLevel')

		con = lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		with con:
			cur = con.cursor()
			cur.execute("INSERT INTO users (name, nik, username, password, level) VALUES (?,?,?,?,?)", (user_dataname, user_dataid, user_datausername, user_datapassword, user_datalevel))
			data = [{
				'Name':user_dataname,
				'NIK':user_dataid,
				'Username':user_datausername,
				'Password':user_datapassword,
				'Level' :user_datalevel
			}]
			con.commit()
			cur.close()
		return jsonify(data)

	def put(self):
		parserWS = reqparse.RequestParser()
		parserWS.add_argument('dataNik')
		parserWS.add_argument('dataName')
		parserWS.add_argument('dataUsername')
		parserWS.add_argument('dataPassword')
		parserWS.add_argument('dataLevel')

		argsWS = parserWS.parse_args()

		user_dataid = argsWS.get('dataNik')
		user_dataname = argsWS.get('dataName')
		user_datausername = argsWS.get('dataUsername')
		user_datapassword = argsWS.get('dataPassword')
		user_datalevel = argsWS.get('dataLevel')

		con = lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		with con:
			cur = con.cursor()
			cur.execute("UPDATE users SET name=?, nik=?, username=?, password=?, level=? WHERE nik = ?", (user_dataname, user_dataid, user_datausername, user_datapassword, user_datalevel, user_dataid))
			data = [{
				'Name':user_dataname,
				'NIK':user_dataid,
				'Username':user_datausername,
				'Password':user_datapassword,
				'Level' :user_datalevel
			}]
			con.commit()
			cur.close()
		return jsonify(data)

	def delete(self):
		parserWS = reqparse.RequestParser()
		parserWS.add_argument('dataNik')

		argsWS = parserWS.parse_args()

		user_dataid = argsWS.get('dataNik')

		con = lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		with con:
			cur = con.cursor()
			cur.execute("DELETE FROM users WHERE nik=(?)",[user_dataid])
			data = [{
			'NIK': user_dataid,
			'msg' : 'NIK '+user_dataid+' berhasil dihapus via METHOD DELETE'
			}]
			con.commit()
			cur.close()
		return jsonify(data)

api.add_resource(userWS,'/userApi', endpoint='userApi/')


class pengajuanWS(Resource):
	def get(self):
		parserWS = reqparse.RequestParser()
		parserWS.add_argument('dataNik')

		argsWS = parserWS.parse_args()

		user_dataid = argsWS.get('dataNik')

		con = lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		with con:
			cur = con.cursor()
			if user_dataid:
				cur.execute("select * from pengajuan where nik=(?)",[user_dataid])
				data = [{
				'NIK':row[0],
				'Judul':row[1],
				'Nik Dosen':row[2],
				'Dosbim':row[3],
				'Sinopsis' :row[5],
				'Status' :row[6]
				}for row in cur.fetchall()]
				con.commit()
				cur.close()
			else:
				cur.execute("select * from pengajuan")
				data = [{
				'NIK':row[0],
				'Judul':row[1],
				'Nik Dosen':row[2],
				'Dosbim':row[3],
				'Sinopsis' :row[5],
				'Status' :row[6]
				}for row in cur.fetchall()]
				con.commit()
				cur.close()	
		return jsonify(data)

	def post(self):
		parserWS = reqparse.RequestParser()
		parserWS.add_argument('dataNik')
		parserWS.add_argument('dataJudul')
		parserWS.add_argument('dataNikDosen')
		parserWS.add_argument('dataDosbim')
		parserWS.add_argument('dataSinopsis')
		parserWS.add_argument('dataStatus')

		argsWS = parserWS.parse_args()

		user_dataid = argsWS.get('dataNik')
		user_datajudul = argsWS.get('dataJudul')
		user_datanikdosen = argsWS.get('dataNikDosen')
		user_datadosbim = argsWS.get('dataDosbim')
		user_datasinopsis = argsWS.get('dataSinopsis')
		user_datastatus = argsWS.get('dataStatus')

		con = lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		with con:
			cur = con.cursor()
			cur.execute("INSERT INTO pengajuan (nik,judul,nik_dosen,dosbim,sinopsis,status) VALUES (?,?,?,?,?,?)",
                  (user_dataid,user_datajudul, user_datanikdosen, user_datadosbim, user_datasinopsis, user_datastatus))
			data = [{
				'NIK':user_dataid,
				'Judul':user_datajudul,
				'Nik Dosen':user_datanikdosen,
				'Dosbim':user_datadosbim,
				'Sinopsis' :user_datasinopsis,
				'Status' :user_datastatus
			}]
			con.commit()
			cur.close()
		return jsonify(data)

	def put(self):
		parserWS = reqparse.RequestParser()
		parserWS.add_argument('dataNik')
		parserWS.add_argument('dataJudul')
		parserWS.add_argument('dataNikDosen')
		parserWS.add_argument('dataDosbim')
		parserWS.add_argument('dataSinopsis')
		parserWS.add_argument('dataStatus')

		argsWS = parserWS.parse_args()

		user_dataid = argsWS.get('dataNik')
		user_datajudul = argsWS.get('dataJudul')
		user_datanikdosen = argsWS.get('dataNikDosen')
		user_datadosbim = argsWS.get('dataDosbim')
		user_datasinopsis = argsWS.get('dataSinopsis')
		user_datastatus = argsWS.get('dataStatus')

		con = lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		with con:
			cur = con.cursor()
			cur.execute("UPDATE pengajuan SET nik=?, judul=?, nik_dosen=?, dosbim=?, sinopsis=?, status=? WHERE nik=?",
				(user_dataid,user_datajudul, user_datanikdosen, user_datadosbim, user_datasinopsis, user_datastatus, user_dataid))
			data = [{
				'NIK':user_dataid,
				'Judul':user_datajudul,
				'Nik Dosen':user_datanikdosen,
				'Dosbim':user_datadosbim,
				'Sinopsis' :user_datasinopsis,
				'Status' :user_datastatus
			}]
			con.commit()
			cur.close()
		return jsonify(data)

	def delete(self):
		parserWS = reqparse.RequestParser()
		parserWS.add_argument('dataNik')

		argsWS = parserWS.parse_args()

		user_dataid = argsWS.get('dataNik')

		con = lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		with con:
			cur = con.cursor()
			cur.execute("DELETE FROM pengajuan WHERE nik=(?)",[user_dataid])
			data = [{
			'NIK': user_dataid,
			'msg' : 'Pengajuan '+user_dataid+' berhasil dihapus via METHOD DELETE'
			}]
			con.commit()
			cur.close()
		return jsonify(data)

api.add_resource(pengajuanWS,'/pengajuanApi', endpoint='pengajuanApi/')

class dosenWS(Resource):
	def get(self):
		parserWS = reqparse.RequestParser()
		parserWS.add_argument('dataNik')

		argsWS = parserWS.parse_args()

		datanik = argsWS.get('dataNik')

		con = lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		with con:
			cur = con.cursor()
			if datanik:
				cur.execute("select * from dosen where nik_dosen=(?)",[datanik])
				data = [{
				'Nik Dosen':row[0],
				'Nama':row[1],
				'Alamat':row[2],
				'Telp':row[3],
				'Fakultas' :row[4],
				'Email' :row[5],
				'Pendidikan Terakhir' :row[6],
				'Prodi' :row[7],
				'Bidang Ilmu' :row[8],
				'Spesialisasi' :row[9],
				'Bhs Pemrograman' :row[10]
				}for row in cur.fetchall()]
				con.commit()
				cur.close()
			else:
				cur.execute("select * from dosen")
				data = [{
				'Nik Dosen':row[0],
				'Nama':row[1],
				'Alamat':row[2],
				'Telp':row[3],
				'Fakultas' :row[4],
				'Email' :row[5],
				'Pendidikan Terakhir' :row[6],
				'Prodi' :row[7],
				'Bidang Ilmu' :row[8],
				'Spesialisasi' :row[9],
				'Bhs Pemrograman' :row[10]
				}for row in cur.fetchall()]
				con.commit()
				cur.close()	
		return jsonify(data)

	def post(self):
		parserWS = reqparse.RequestParser()
		parserWS.add_argument('dataNik')
		parserWS.add_argument('dataNama')
		parserWS.add_argument('dataAlamat')
		parserWS.add_argument('dataTelp')
		parserWS.add_argument('dataFakultas')
		parserWS.add_argument('dataEmail')
		parserWS.add_argument('dataPendidikan')
		parserWS.add_argument('dataProdi')
		parserWS.add_argument('dataBidIlmu')
		parserWS.add_argument('dataSpesialisasi')
		parserWS.add_argument('dataBhspemrograman')

		argsWS = parserWS.parse_args()

		datanik = argsWS.get('dataNik')
		datanama = argsWS.get('dataNama')
		dataalamat = argsWS.get('dataAlamat')
		datatelp = argsWS.get('dataTelp')
		datafakultas = argsWS.get('dataFakultas')
		dataemail = argsWS.get('dataEmail')
		datapendidikan = argsWS.get('dataPendidikan')
		dataprodi = argsWS.get('dataProdi')
		databidilmu = argsWS.get('dataBidIlmu')
		dataspesialisasi = argsWS.get('dataSpesialisasi')
		databhspemrograman = argsWS.get('dataBhspemrograman')

		con = lite.connect("skripsiDB.db")
		con.row_factory = lite.Row
		with con:
			cur = con.cursor()
			cur.execute("INSERT INTO dosen (nik_dosen,dosbim,alamat,telp,fakultas,email_dosbim,pend_terakhir,prodi,bid_ilmu,spesialisasi,bhs_program) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (datanik, datanama, dataalamat, datatelp, datafakultas, dataemail, datapendidikan, dataprodi, databidilmu, dataspesialisasi, databhspemrograman))
			data = [{
				'Nik Dosen':datanik,
				'Nama':datanama,
				'Alamat':dataalamat,
				'Telp':datatelp,
				'Fakultas' :datafakultas,
				'Email' :dataemail,
				'Pendidikan Terakhir' :datapendidikan,
				'Prodi' :dataprodi,
				'Bidang Ilmu' :databidilmu,
				'Spesialisasi' :dataspesialisasi,
				'Bhs Pemrograman' :databhspemrograman
			}]
			con.commit()
			cur.close()
		return jsonify(data)

api.add_resource(dosenWS,'/dosenApi', endpoint='dosenApi/')



app.secret_key="aaabbbccc"

if __name__ == '__main__':
    app.run(
    	debug=True
    )