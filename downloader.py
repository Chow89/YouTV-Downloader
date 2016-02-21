import datetime
import inspect
import os

from bs4 import BeautifulSoup
import dateutil.parser
import requests

LOGIN_EMAIL = ""
LOGIN_PASSWORD = ""
PREMIUM = False
SAVEPATH = ""
CHUNKSIZE = 8 * 1024 * 1024     # 8 MB
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
                    if PREMIUM:     # all records in last 7 days
                        log("Start downloading " + rec['title'] + " from " + rec['channel_name'] + ".")
                        download(s, (getremotefileurl(s, rec['url']), makefilename(rec, line)))
                    else:
                        if start > now - 24 * 60 * 60:  # all records within last 24 hours
                            log("Start downloading " + rec['title'] + " from " + rec['channel_name'] + ".")
                            download(s, (getremotefileurl(s, rec['url']), makefilename(rec, line)))


def makefilename(rec, line):
    return rec['starts_at'][0:19].replace("T", "_").replace(":", "-") + "_" + line.replace(" ", "_") + "_" + \
           rec['channel_name'].lower().replace(" ", "-") + ".mp4"


def getremotefileurl(s, url):
    soup = BeautifulSoup(s.get(url + "/streamen").text, 'html.parser')
    sources = soup.find_all('source')
    try:
        return sources[-1]['src']
    except:
        log("No source file found at " + url + "/streamen")
        return ""


def download(s, url):
    if not url[0] == "":
        if not os.path.isfile(SAVEPATH + url[1]):
            log("File from " + url[0] + " will be saved at " + SAVEPATH + url[1])
            video = s.get(url[0], stream=True)
            with open(SAVEPATH + url[1], "wb") as file:
                for chunk in video.iter_content(chunk_size=CHUNKSIZE):
                    if chunk:
                        file.write(chunk)
        else:
            log("File " + url[1] + " already exists.")


def log(message):
    f = open(BASEPATH + "/log.log", "a")
    f.write(message + "\n")
    f.close()


run()