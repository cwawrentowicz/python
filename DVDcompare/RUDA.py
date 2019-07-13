# -*- coding: cp1250 -*-
import os
import sys
import sqlite3
import hashlib
import datetime
import subprocess

def create_hash(ffile):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(ffile, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print('error1: ' + str(e))
    return None

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print('error2: ' + str(e))
 

def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles


def insert(database,ppath,hhash,i,bbasename):
    conn = create_connection(database)
    with conn:
        sql = ''' INSERT INTO orgin(path,hash,id,basename)
              VALUES(?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (ppath,hhash,i,bbasename))
        return cur.lastrowid


def main():

    ############# Dane do raportu ########################
    
    jednostka = "Regionalna w Białymstoku"
    sygnatura =  input("Sygnatura:")
    oznaczenie = input("Wpisz oznaczenie płyty:")
    osoba = input("Osoba:")
    ############# nazwa pliku bazy danych SQLite #########
    database='C:\\sqlite\\hashDB.db'
    ############# plik raportu ###########################
    txtfile='c:\\python36\\wyniki.txt'
    ############# Pierwszy napęd DVD #####################
    dirName = 'g:\\';
   
    ######################################################

   
    f=open( txtfile,'w') 
    f.write("********************************************************************\n")
    f.write("* autor skryptu: C. Wawrentowicz                                   *\n")
    f.write("* wersja z dnia: 17.05.2019                                        *\n")
    f.write("* Python 3.6                                                       *\n")
    f.write("* skrypt wylicza sumy kontrolne MD5 plików                         *\n")
    f.write("********************************************************************\n")   
    f.write("\n")
    f.write("Jednostka: " + jednostka + "\n");
    f.write("Sygnatura sprawy: " + sygnatura + "\n");
    f.write("Oznaczenie płyty: " + oznaczenie + "\n");
    f.write("Osoba wykonująca czynności: " + osoba + "\n");
    f.write("Data wykonania skryptu: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + "\n");
    f.write("\n")
    

    print("start")
    sql_create_orgin_table = """ CREATE TABLE IF NOT EXISTS orgin (
                                        id int,
                                        path text NOT NULL,
                                        basename text NOT NULL,
                                        hash text NOT NULL
                                ); """
    
    conn = create_connection(database)
    if conn is not None:       
        create_table(conn,"DROP TABLE IF EXISTS orgin;")
        create_table(conn, sql_create_orgin_table)
    print("pobieranie  listy plików z oryginału, może to chwilę potrwać")
    allFiles = getListOfFiles(dirName)
    i=1
    for entry in allFiles:
       print(str(i) + " " + entry)
       insert(database,entry[2:] ,create_hash(entry),i,os.path.basename(entry))
       i=i+1
    cursor = conn.cursor()
    cursor.execute('''SELECT path, hash FROM orgin;''')    
    all_rows = cursor.fetchall()
    f.write ("ścieżka do pliku :  suma kontrolna MD5\n")
    j=1
    for row in all_rows:
        s='{0} : {1}'.format(row[0], row[1])
        print(s)
        f.write (str(j) + ")  " + s + "\n")
        j=j+1
    f.write("\n")
    f.write("Data wykonania skryptu: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + "\n");
    f.write("--- koniec wydruku ---");
    
     
    f.close()


    subprocess.Popen(['Notepad.exe ' , txtfile])

    
if __name__ == '__main__':
    main()
    
