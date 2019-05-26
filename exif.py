import argparse
import subprocess
import os
import datetime
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import webbrowser


#https://www.codingforentrepreneurs.com/blog/extract-gps-exif-images-python/
class ImageData():

    exif_data = None
    image = None

    def __init__(self, entry):
        try:
            self.image = Image.open(entry)
            self.get_exif_data()
            self.date = self.get_date_time()
            super().__init__()
        except:
             print ("błąd 0 odczytu pliku: " + entry)

    def get_exif_data(self):
        try:
            exif_data = {}
            #.info['parsed_exif']
            info = self.image._getexif()
            if info:
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    if decoded == "GPSInfo":
                        gps_data = {}
                        for t in value:
                            sub_decoded = GPSTAGS.get(t, t)
                            gps_data[sub_decoded] = value[t]
                        exif_data[decoded] = gps_data
                    else:
                        exif_data[decoded] = value
            self.exif_data = exif_data
            return exif_data
        except:
            print( "błąd 1 w odczycie Exif w pliku " )

    def get_if_exist(self, data, key):
        if key in data:
            return data[key]
        return None

    def get_date_time(self):
        if 'DateTimeOriginal' in self.exif_data:
            date_and_time = self.exif_data['DateTimeOriginal']
            return date_and_time 

    def convert_to_degress(self, value):
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)

    def get_lat_lng(self):
        lat = None
        lng = None
        try:
            exif_data = self.get_exif_data()         
            if "GPSInfo" in exif_data:      
                gps_info = exif_data["GPSInfo"]
                gps_latitude = self.get_if_exist(gps_info, "GPSLatitude")
                gps_latitude_ref = self.get_if_exist(gps_info, 'GPSLatitudeRef')
                gps_longitude = self.get_if_exist(gps_info, 'GPSLongitude')
                gps_longitude_ref = self.get_if_exist(gps_info, 'GPSLongitudeRef')
                if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                    lat = self.convert_to_degress(gps_latitude)
                    if gps_latitude_ref != "N":                     
                        lat = 0 - lat
                    lng = self.convert_to_degress(gps_longitude)
                    if gps_longitude_ref != "E":
                        lng = 0 - lng
            return lat, lng
        except:
            print("Błąd 0")

def getListOfFilesPic(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:        
            fullPath = os.path.join(dirName, entry)
            if os.path.isdir(fullPath):
                allFiles = allFiles + getListOfFilesPic(fullPath)
            else:
                if entry.endswith(".jpg") or  entry.endswith(".png"):
                    allFiles.append(fullPath)              
    return allFiles

def thumb_nail(i, folder,entry):
    pic_size = (320, 220)
    try:
        im= Image.open(entry)
        im.thumbnail(pic_size, Image.ANTIALIAS)
        im.save(folder + "/" + str(i) + ".jpg", 'JPEG', quality=80)
        return 0
    except:
        print("Błąd 2 przy tworzeniu miniatury")
        return 1

def create_hash(ffile):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(ffile, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()
    

def main():

    jednostka = "Regionalna w Białymstoku"
    sygnatura = "" #  input("Sygnatura sprawy:")
    oznaczenie = "" # input("Oznaczenie:")
    osoba = "" # input("Osoba:")
    print("Wczytuję listę plików ......")
    #files_list = getListOfFilesPic("C:\\Users\\c.wawrentowicz\\pictures\\zdjęcia Kasi\\Ladek")
    files_list = getListOfFilesPic("C:\\Users\\c.wawrentowicz\\pictures\\scan")
    #f=open( "wyniki.txt",'w')
   
    folder = os.getcwd() + "\\" + str(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(folder +"\\images"):
        os.makedirs(folder + "\\images") 
    filename = folder + "\\" + "go.html"
    print("Raport zapisuję do folderu: " + folder)
    f=open( filename,'w')
    f.write("<head><style>table, th, td { border: 1px solid black;} tr:nth-child(even) { background-color: #dddddd;}</style>\n<title>EXIF</title>\n</head>\n")
    f.write("<body>\n")
    f.write("Jednostka: " + jednostka + "<br>\n")
    f.write("Sygnatura sprawy: " + sygnatura + "<br>\n")
    f.write("Oznacznie: " + oznaczenie + "<br>\n")
    f.write("Osoba wykonująca czynności: " + osoba + "<br><br>\n");
    f.write("<table>\n")
    f.write("<thead><tr><th>Lp</th><th>Nazwa plku</th><th>Scieżka</th><th>Data utworzenia</th><th>Suma kontrolna</th><th>Miniatura</th><th>Lokalizacja (szer. / dł.)</th><th>Otwórz Google maps</th></tr></thead>\n")
    f.write("<tbody>\n")
    i=1 
    for entry in files_list:
        print("|" , end="")
        meta_data =  ImageData(entry)
        latlng =meta_data.get_lat_lng()
        if   latlng != (None, None):
            chk = thumb_nail(i,folder + "\\images", entry)
            if chk ==0:
                f.write("<tr><td>" + str(i) + "</td><td>" + os.path.basename(entry) +  "</td><td><a href='" + entry  + "'>" + entry + "</a></td><td>" + str(meta_data.get_date_time()) + "</td><td>" + create_hash(entry) + "</td><td>" + "<img src='images\\" + str(i) + ".jpg" + "' style='height: 220px; width: 320px'/> " +  "</td><td>" +  str(latlng[0]) + " / "    + str(latlng[1]) + "</td><td><a href='https://maps.google.com/?q=" + str(latlng[0]) + "," + str(latlng[1]) +  "'> >>> </a></td></tr>\n")
                print (entry + " " + str(latlng)  + "\n")            
                #print(str(latlng) + " " + entry)
                i=i+1
    f.write("</tbody>\n")
    f.write("</table>\n")
    f.write("<small>autor skryptu: C. Wawrentowicz<br>\n")
    f.write("wersja z dnia: 25.05.2019<br>\n")
    f.write("Python 3.6<br></small>\n")

    f.write("</body>\n</html>")
    f.close()
    webbrowser.open(folder + "\\" + "go.html")
if __name__ == '__main__':
    main()             


