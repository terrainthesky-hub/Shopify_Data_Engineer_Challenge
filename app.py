# Importing the required packages/libraries
from flask import Flask,request,render_template,redirect,url_for,session, flash, jsonify
import  pymysql
import re
from binary_conversion import main, read_blob_data, insert_into_database, write_to_file, convert_into_binary
from werkzeug.utils import secure_filename
import os
import sqlite3
import bcrypt
import hashlib
import itertools
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf import FlaskForm
from wtforms import SubmitField
import urllib.request

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r'C:\lambda\Job coding challenge\User-login-GUI-using-python-Flask-web-framework-mySQL-database-main\User-login-GUI-using-python-Flask-web-framework-mySQL-database-main'

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# app.config['UPLOAD_PATH'] = 


@app.route('/', methods=['GET', 'POST'])
def login():

    conn = sqlite3.connect('login.db')

    cursor = conn.cursor()

    msg = ''
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        
        username = request.form['username']
        password = request.form['password']

        cursor.execute(f"SELECT password FROM logins where username = '{username}'")
        if cursor.fetchone() == None:
            return redirect("register.html")
        else:
            hashAndSalt = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            valid = bcrypt.checkpw(password.encode('utf-8'), hashAndSalt)
            return render_template('upload.html')

    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = sqlite3.connect('login.db')

    cursor = conn.cursor()


    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:

        fullname = request.form['fullname']
       
        username = request.form['username']
        password = request.form['password']
        confirmpasswd = request.form['re_pass']
        email = request.form['email']


        cursor.execute(f"SELECT username FROM logins where username = '{username}'")
        account = cursor.fetchone()

        if account == username:
            msg = 'user name already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form completely!'
        elif confirmpasswd != password:
            msg = "Password mismatch, Provide confirm password as same as password;"
        else:
            hashAndSalt = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('INSERT INTO logins (fullname, username, password, email) VALUES (?, ?, ?, ?)', (fullname, username, hashAndSalt, email))
            conn.commit()
            msg = 'You have successfully registered!'


    return render_template('register.html', msg=msg)


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    conn = sqlite3.connect('login.db')

    cursor = conn.cursor()

    msg=''

    if request.method == "POST" and 'username' in request.form and 'email' in request.form:
        uname=request.form['username']
        email=request.form['email']

        cursor.execute('select * from logins where username=%s and email=%s',(uname,email))
        account=cursor.fetchone()

        if account:
            return redirect(url_for('change'))
        else:
            msg = "User name and email are not match"

    else:
        msg = "Invalid"

    return render_template('forgot.html', msg=msg)


@app.route('/change',methods=['GET', 'POST'])
def change():
    conn = sqlite3.connect('login.db')

    cursor = conn.cursor()

    msg=''

    if request.method=='POST' and 'passwd' in request.form and 'confmpasswd' in request.form:
        password=request.form['passwd']
        confirmpasswd=request.form['confmpasswd']


        if password == confirmpasswd:
            cursor.execute("update logins set password = %s where username = %s",(password,session['username']))
            conn.commit()
            msg = "Password changed successfully"
        else:
            msg = "New password and confirm password are not matched"

    return render_template('change.html',msg=msg)

@app.route('/success')
def success():
    return render_template('success.html')


# @app.route('/upload')
# def upload_file():
#    return render_template('upload.html')


# class FileUploadForm(FlaskForm):
#     photo_or_pdf_file = FileField('photo', validators=[
#         FileRequired(),
#         FileAllowed(['png', 'pdf', 'jpg'], "wrong format!")
#     ])
#     submit = SubmitField('Upload')


# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
#     form = FileUploadForm()
#     if form.validate_on_submit():
#         f = form.photo_or_pdf_file.data
#         return f.filename
#     return render_template('upload.html', form=form)


# class UploadForm(FlaskForm):
#     photo = FileField('Image', validators=[
#         FileRequired(),
#         FileAllowed(['jpg', 'png'], 'Image only!')
#     ])
#     submit = SubmitField('Submit')


# @app.route('/uploader', methods=['GET','POST'])
# def upload():
#     form = UploadForm()
#     if form.validate_on_submit() and 'photo' in request.files:
#         for f in request.files.getlist('photo'):
#             filename = secure_filename(f.filename)
#             f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
#             return redirect('success.html')
#     return render_template('upload.html', form=form)
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# def allowed_file(filename):
# 	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/upload', methods=['POST'])
# def upload_file():
# 	if request.method == 'POST':
#         # check if the post request has the files part
# 		if 'files[]' not in request.files:
# 			flash('No file part')
# 			return redirect(request.url)
# 		files = request.files.getlist('files[]')
# 		for file in files:
# 			if file and allowed_file(file.filename):
# 				filename = secure_filename(file.filename)
# 				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
# 		flash('File(s) successfully uploaded')
# 	return redirect('/success')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'files[]' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	
	files = request.files.getlist('files[]')
	
	errors = {}
	success = False
	
	for file in files:		
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			success = True
		else:
			errors[file.filename] = 'File type is not allowed'
	
	if success and errors:
		errors['message'] = 'File(s) successfully uploaded'
		resp = jsonify(errors)
		resp.status_code = 206
		return resp
	if success:
		resp = jsonify({'message' : 'Files successfully uploaded'})
		resp.status_code = 201
		return resp
	else:
		resp = jsonify(errors)
		resp.status_code = 400
		return resp



# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# # Get current path
# path = os.getcwd()
# # file Upload
# UPLOAD_FOLDER = os.path.join(path, 'uploads')

# # Make directory if uploads is not exists
# if not os.path.isdir(UPLOAD_FOLDER):
#     os.mkdir(UPLOAD_FOLDER)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Allowed extension you can set your own
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/upload')
# def upload_form():
#     return render_template('upload.html')


# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if request.method == 'POST':

#         if 'files[]' not in request.files:
#             flash('No file part')
#             return redirect(request.url)

#         files = request.files.getlist('files[]')

#         for file in files:
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

#         flash('File(s) successfully uploaded')
#         return redirect('/')

# @app.route('/uploader', methods=['GET','POST'])
# def upload_filer():
#     # if request.method == 'POST':
        
#         # if 'files[]' not in request.files:
#         #     return redirect(request.url)

#         files = request.files.getlist('files[]')

#         for file in files:
#             if file and allowed_file(file.filename) and file.endswith("jpg"):
#                 filename = secure_filename(file.filename)
#                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # counter = 0
        # jpgfiles = []
        # pngfiles = []
        # print(os.getcwd())
        # directory = os.getcwd()
        # for dirpath, subdirs, files in os.walk(directory):
        #     for x in files:
        #         if x.endswith(".jpg"):
        #             jpgfiles.append(x)
        #             file_path_name = jpgfiles[counter]
        #             file_blob = convert_into_binary(file_path_name)
        #             last_updated_entry = insert_into_database(file_path_name, file_blob)
        #             read_blob_data(last_updated_entry)
        #             counter += 1
        #         if x.endswith(".png"):
        #             pngfiles.append(x)
        #             file_path_name = pngfiles[counter]
        #             file_blob = convert_into_binary(file_path_name)
        #             last_updated_entry = insert_into_database(file_path_name, file_blob)
        #             read_blob_data(last_updated_entry)
        #             counter += 1
        # return render_template('success.html')
     
      



# from flask_autoindex import AutoIndex

# ppath = r"C:\lambda\Job coding challenge\User-login-GUI-using-python-Flask-web-framework-mySQL-database-main\User-login-GUI-using-python-Flask-web-framework-mySQL-database-main" # update your own parent directory here

# AutoIndex(app, browse_root=ppath)
	
# @app.route('/uploader', methods = ['GET', 'POST'])
# def upload_files():
#    if request.method == 'POST':
#         f = request.files['file']  
#         f.save(f.filename)  
#         counter = 0
#         jpgfiles = []
#         pngfiles = []
#         for dirpath, subdirs, files in os.walk():
#             for x in files:
#                 if x.endswith(".jpg"):
#                     jpgfiles.append(os.path.join(dirpath, x))
#                     file_path_name = jpgfiles[counter]
#                     file_blob = convert_into_binary(file_path_name)
#                     last_updated_entry = insert_into_database(file_path_name, file_blob)
#                     read_blob_data(last_updated_entry)
#                     counter += 1
#                 if x.endswith(".png"):
#                     pngfiles.append(os.path.join(dirpath, x))
#                     file_path_name = pngfiles[counter]
#                     file_blob = convert_into_binary(file_path_name)
#                     last_updated_entry = insert_into_database(file_path_name, file_blob)
#                     read_blob_data(last_updated_entry)
#                     counter += 1
#     return render_template("success.html", name = f.filename) 
		

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=5000,debug=False,threaded=True)
    app.run(debug=True)
