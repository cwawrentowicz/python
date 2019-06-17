import os
import sys
import sqlite3
import hashlib
import datetime


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print('error1: ' + str(e))
    return None


def extract_picture(cursor, id,thread_id, filename):
    sql ="SELECT _id,thread_id, attachment_id, attachment_data, attachment_type FROM  data  where  _id = :id and thread_id = :idt"
    param = {'id': id, 'idt':thread_id}
    cursor.execute(sql, param)
    rows =cursor.fetchall()
    s=""
    p=""
    for  r in rows:
        p = str(r[0]) + "-" + str(r[1]) + "-" + str(r[2]) + ".jpg"        
        with open(p, 'wb') as output_file:
            output_file.write(r[3])
            s = s + "<img src='" + p + "' style='height: 400px; width: 400px'/> "
    return s



def extract_mmssms(cursor,filename):
    sql ="SELECT _id, body, address,  case when length(date) =10 then datetime(date,'unixepoch','localtime')  else datetime(date/1000,'unixepoch','localtime') end as data1, case when date_sent =0 then ''  else datetime(date_sent/1000,'unixepoch','localtime') end as data2,type,thread_id, service_center FROM 'mmssms'   order by  thread_id,  data1, _id "
    cursor.execute(sql)
    rows=cursor.fetchall()
    f=open( filename,'a')
    #f.write("<table style='border: 1px solid #808080' >\n")
    f.write("<table>\n")
    f.write("<thead><tr><th>ID</th><th>TreĹ›Ä‡</th><th>Adres</th><th>Data</th><th>Data wysĹ‚ania</th><th>Typ</th></tr></thead>\n")
    f.write("<tbody>\n")
    for  r in rows:
        pic=""
        #print(r[7])
        if len(r[1])==0 :
            pic= extract_picture(cursor, r[0],r[6], filename)
            print(r[1] + " " + pic)
        #else:
        #    pic= extract_picture(cursor, r[0],r[6], filename)
        f.write("<tr>\n")
        if r[5]==1:
            f.write("<td>" + r[0] + " " + str(r[6]) + "</td><td style='text-align: left; background-color: #EEEEEE;'>" + r[1] + "</td><td>" + str(r[2]) + "</td><td>" + str(r[3]) + "</td><td>" + str(r[4]) + "</td><td>" + str(r[5]) +  "</td><td>" + pic + "</td>\n")
        else:
            f.write("<td>" + r[0] + " " + str(r[6]) + "</td><td style='text-align: right; background-color: white;'>" + r[1] + "</td><td>" + str(r[2]) + "</td><td>" + str(r[3]) + "</td><td>" + str(r[4]) + "</td><td>" + str(r[5]) +  "</td><td>" + pic + "</td>\n")
        f.write("</tr>\n")
    f.write("</tbody>\n")
    f.write("</table>\n")
    f.close()
    return

#### START
#### 16.06.2019
#### scieżka do bazy danych 
database='C:\\!m2\\Android Image - 2019-05-17 21-14-42\\samsung SM-G935F Quick Image\\Agent Data\\agent_mmssms.db'
####
conn = create_connection(database)
if conn is not None:
    filename ="mmssms.html"
    f=open( filename,'w')
    f.write("<head><style>table, th, td { border: 1px solid black;}</style>\n<title>MMSSMS</title>\n</head>\n")
    f.write("<body>\n")
    f.write("<table>\n")
    f.close()
    cur = conn.cursor()
    extract_mmssms(cur,filename)
    f=open( filename,'a')
    f.write("</body>\n</html>")
    f.close()

conn.close()



