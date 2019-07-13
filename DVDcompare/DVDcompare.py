# -*- coding: cp1250 -*-
import os
import sys
import sqlite3
import hashlib
import datetime
import subprocess
import zlib
import binascii


def create_hash1(filename):
    buf = open(filename,'rb').read()
    buf = (binascii.crc32(buf) & 0xFFFFFFFF)
    print(buf)
    return "%08X" % buf


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
    sygnatura = "11.2016"
    oznaczenie = input("Wpisz oznaczenie płyty:")
    osoba = "Cezary Wawrentowicz"
    ############# nazwa pliku bazy danych SQLite #########
    database='C:\\sqlite\\hashDB.db'
    ############# plik raportu ###########################
    txtfile='c:\\python36\\wyniki.txt'
    ############# Pierwszy napęd DVD #####################
    dirName = 'f:\\';
    ############# Drugi napęd DVD ########################
    dirNameCopy = 'f:\\';

    ######################################################

    if dirName ==  dirNameCopy:
        print("Błąd:napęd z oryginałem i kopią ma to samo oznaczenie !!! ")
        #sys.exit()

    raport = input("Typ raportu 0 - prosty, 1 - dokładny [1]:")
    raport = raport or "1"

   
    f=open( txtfile,'w') 
    f.write("********************************************************************\n")
    f.write("* autor skryptu: C. Wawrentowicz                                   *\n")
    f.write("* wersja z dnia: 08.05.2019                                        *\n")
    f.write("* skrypt porównuje zawartość dwóch płyt sprawdzając pełne ścieżki  *\n")
    f.write("* do plików   i ich  sumy kontrolne                                *\n") 
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
    print("pobieranie  listy plików z kopii, może to chwilę potrwać")
    allFiles = getListOfFiles(dirNameCopy)
    i=1000001
    for entry in allFiles:
       print(str(i-1000000) + " " + entry)
       insert(database,entry[2:] ,create_hash(entry),i,os.path.basename(entry))
       i=i+1
    print("")
    print("---------------- PLIKI RÓŻNIĄCE SIĘ W ORYGINALE I KOPII --------------")
    print("----------------------------------------------------------------------")
    f.write("--------------------------------------------------------------------\n")
    f.write("-------------- PLIKI RÓŻNIĄCE SIĘ W ORYGINALE I KOPII --------------\n")
    f.write("--------------------------------------------------------------------\n")
    print("")
    cursor = conn.cursor()
    cursor.execute('''SELECT path, hash, sum(1) FROM orgin group by path, hash having sum(1)=1''')    
    all_rows = cursor.fetchall()
    if (len(all_rows))==0:
        print(" *** nie znaleziono różnic ***")
        f.write (" *** nie znaleziono różnic ***\n")
    else:
        f.write ("ścieżka do pliku :  suma kontrolna MD5\n")
        for row in all_rows:
            s = '{0} : {1}'.format(row[0], row[1])
            print(s)
            f.write (s + "\n")
        f.write("Niepowodzenie: brak zgodności  oryginału i kopii\n")
        print("Niepowodzenie: brak zgodności  oryginału i kopii")
  
    if raport == "1":
        print("")
        print("----------------------------- PLIKI POPRAWNIE SKOPIOWANE-----------------")
        print("-------------------------------------------------------------------------")
        f.write("---------------------------------------------------------------------\n")
        f.write("----------------------------- PLIKI POPRAWNIE SKOPIOWANE-------------\n")    
        f.write("---------------------------------------------------------------------\n")
        print("")
        cursor = conn.cursor()
        cursor.execute('''SELECT path, hash, sum(1) FROM orgin group by path, hash having sum(1)=2''')    
        all_rows = cursor.fetchall()
        i=1
        f.write ("ścieżka do pliku :  suma kontrolna MD5\n")
        for row in all_rows:
            s='{0} : {1}'.format(row[0], row[1])
            print(s)
            f.write (str(i) + ")  " + s + "\n")
            i=i+1
        f.write("\n")
        print("Sukces: zgodność oryginału i kopii")
        f.write("Sukces: zgodność oryginału i kopii\n")
        f.write("Data wykonania skryptu: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + "\n");
        f.write("--- koniec wydruku ---");
    else:
        cursor.execute('''SELECT  hash  FROM orgin where id<1000000 order by hash''')    
        all_rows = cursor.fetchall()
        i=0
        h =""
        hash = hashlib.md5()
        for row in all_rows:
            h =  h+ row[0]
            hash.update(str(h).encode('utf-16'))
            hh = hash.hexdigest()
            h=hh
            i=i+1
            print(str(i) + " " + row[0])
        h1 = h

        cursor.execute('''SELECT  hash  FROM orgin where id>1000000 order by hash''')    
        all_rows = cursor.fetchall()
        j=0
        h =""
        hash = hashlib.md5()
        for row in all_rows:
            h =  h+ row[0]
            hash.update(str(h).encode('utf-16'))
            hh = hash.hexdigest()
            h=hh
            j=j+1
            print(str(j) + " " + row[0])
        h2=h
        print("")
        print(h1 + "  "  + str(i))
        print(h2 + "  "  + str(j))
        f.write("\n")
        f.write("Oryginał suma kontrolna " + h1 + " ilość plików: " + str(i) + "\n")
        f.write("Kopia    suma kontrolna " + h2 + " ilość plików: " + str(j) + "\n")

        if (h1==h2) and (i==j):            
            print("Sukces: zgodność oryginału i kopii")
            f.write("Sukces: zgodność oryginału i kopii\n")
        else:    
            print("Niepowodzenie: brak zgodności  oryginału i kopii")
            f.write("Niepowodzenie: brak zgodności  oryginału i kopii\n")
        f.write("\n")
        f.write("Data wykonania skryptu: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + "\n");
        f.write("--- koniec wydruku ---");
     
    f.close()


    subprocess.Popen(['Notepad.exe ' , txtfile])

    
if __name__ == '__main__':
    main()
    
