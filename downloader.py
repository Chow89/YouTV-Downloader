import datetime
import inspect
import os
import platform

from bs4 import BeautifulSoup
import dateutil.parser
import requests


LOGIN_EMAIL = ""
LOGIN_PASSWORD = "
PREMIUM = False
SAVEPATH = "" if platform.system() == "Windows" else ""
CHUNKSIZE = 8 * 1024 * 1024  # 8 MB
BASEPATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def run():
    init()
    s = requests.Session()
    login(s)
    getallrecords(s)


def init():
    if not os.path.isdir(SAVEPATH):
        os.makedirs(SAVEPATH)


def login(s):
    s.post("https://youtv.de/login", {"session[email]": LOGIN_EMAIL, "session[password]": LOGIN_PASSWORD})


def getallrecords(s):
    f = open(BASEPATH + "/serien.txt")
    for line in f:
        if not line.startswith("#"):
            line = line.replace("\n", "").replace("\r", "")
            json = s.get("https://youtv.de/api/v2/broadcasts/search?q=" + line).json()
            for rec in json['broadcasts']:
                start = dateutil.parser.parse(rec['starts_at']).timestamp()
                now = datetime.datetime.now().timestamp()
                if start < now:
                    if PREMIUM:  # all records in last 7 days
                        log("Start downloading " + cleanstring(str(rec)))
                        download(s, (getremotefileurl(s, rec['url']), makefilename(rec)))
                    else:
                        if start > now - 24 * 60 * 60:  # all records within last 24 hours
                            log("Start downloading " + cleanstring(str(rec)))
                            download(s, (getremotefileurl(s, rec['url']), makefilename(rec)))


def cleanstring(s):
    return s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss").replace("Ä", "Ae").replace("Ö",
            "Oe").replace("Ü", "Ue").replace(" ", "_")


def makefilename(rec):
    if rec['series_number'] is None or rec['series_season'] is None:
        return rec['starts_at'][0:19].replace("T", "_").replace(":", "-") + "_" + cleanstring(rec['title']) + "_" + \
               rec['channel_name'].lower().replace(" ", "-") + ".mp4"
    else:
        return "S" + makedoubledigit(rec['series_season']) + "E" + makedoubledigit(
            rec['series_number']) + "_" + cleanstring(rec['title']) + ".mp4"


def makedoubledigit(n):
    if n > 9:
        return str(n)
    else:
        return "0" + str(n)


def getremotefileurl(s, url):
    soup = BeautifulSoup(s.get(url + "/streamen").text, 'html.parser')
    sources = soup.find_all('source')
    # FIXME: sort the list by resolution and take the first element
    if len(sources) == 4:
        return sources[2]['src']
    elif len(sources) == 2:
        return sources[1]['src']
    else:
        log("No source data found.\n")
        return ""


def download(s, url):
    if not url[0] == "":
        if not os.path.isfile(SAVEPATH + url[1]):
            log("File from " + url[0] + " will be saved at " + SAVEPATH + url[1] + "\n")
            video = s.get(url[0], stream=True)
            with open(SAVEPATH + url[1], "wb") as file:
                for chunk in video.iter_content(chunk_size=CHUNKSIZE):
                    if chunk:
                        file.write(chunk)
        else:
            log("File " + url[1] + " already exists.\n")


def log(message):
    f = open(BASEPATH + "/log.log", "a")
    f.write(message + "\n")
    f.close()


run()