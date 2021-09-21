import os
import sqlite3
from sqlite3 import Error
from flask import Blueprint, render_template, request
import os
import glob

# rootdir = r'C:\lambda\Job coding challenge\sqlite3_blob_data\data\train\forest'

def read_blob_data(entry_id):
  try:
    conn = sqlite3.connect('app.db')
    cur = conn.cursor()
    print("[INFO] : Connected to SQLite to read_blob_data")
    sql_fetch_blob_query = """SELECT * from uploads where id = ?"""
    cur.execute(sql_fetch_blob_query, (entry_id,))
    record = cur.fetchall()
    for row in record:
      converted_file_name = row[1]
      photo_binarycode  = row[2]
      last_slash_index = converted_file_name.rfind("/") + 1
      final_file_name = converted_file_name[last_slash_index:] 
      write_to_file(photo_binarycode, final_file_name)
      print("[DATA] : Image successfully stored on disk. Check the project directory. \n")
    cur.close()
  except sqlite3.Error as error:
    print("[INFO] : Failed to read blob data from sqlite table", error)
  finally:
    if conn:
        conn.close()


def insert_into_database(file_path_name, file_blob): 
  try:
    conn = sqlite3.connect('app.db')
    print("[INFO] : Successful connection!")
    cur = conn.cursor()
    sql_insert_file_query = '''INSERT INTO uploads(file_name, file_blob)
      VALUES(?, ?)'''
    cur = conn.cursor()
    cur.execute(sql_insert_file_query, (file_path_name, file_blob, ))
    conn.commit()
    print("[INFO] : The blob for ", file_path_name, " is in the database.") 
    last_updated_entry = cur.lastrowid
    return last_updated_entry
  except Error as e:
    print(e)
  finally:
    if conn:
      conn.close()
    else:
      error = "Oh shucks, something is wrong here."

def write_to_file(binary_data, file_name):
    with open(file_name, 'wb') as file:
        file.write(binary_data)
        print("[DATA] : The following file has been written to the project directory: ", file_name)

def convert_into_binary(file_path_name):
    with open(file_path_name, "rb") as file:
        binary = file.read()
    return binary


def main():
    counter = 0
    jpgfiles = []
    pngfiles = []
    for dirpath, subdirs, files in os.walk(r'C:\lambda\Job coding challenge\User-login-GUI-using-python-Flask-web-framework-mySQL-database-main\User-login-GUI-using-python-Flask-web-framework-mySQL-database-main'):
        for x in files:
            if x.endswith(".jpg"):
                jpgfiles.append(os.path.join(dirpath, x))
                file_path_name = jpgfiles[counter]
                file_blob = convert_into_binary(file_path_name)
                last_updated_entry = insert_into_database(file_path_name, file_blob)
                read_blob_data(last_updated_entry)
                counter += 1
            if x.endswith(".png"):
                pngfiles.append(os.path.join(dirpath, x))
                file_path_name = pngfiles[counter]
                file_blob = convert_into_binary(file_path_name)
                last_updated_entry = insert_into_database(file_path_name, file_blob)
                read_blob_data(last_updated_entry)
                counter += 1

if __name__ == "__main__":
  main()