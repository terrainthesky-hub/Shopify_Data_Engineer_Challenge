import sqlite3

conn = sqlite3.connect('login.db')

conn.execute('CREATE TABLE logins (fullname TEXT, username TEXT, password TEXT, email TEXT)')
conn.close()