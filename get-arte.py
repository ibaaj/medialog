# -*- coding: utf-8 -*-
#
# Arte has really good content
# sadly, the rss feed isn't relevant and updated enough
# so we must scrap
# it seems to change often in a day so I launch this script every 3 hours...
# I got several issue with python3 so it needs to be loaded with python2
# ...

import urllib
from bs4 import BeautifulSoup
import re
import json
from math import ceil
from datetime import datetime
from time import mktime, sleep
import itertools
import locale
import pygsheets

data = {}
"""

excludedVideos = [
    u"28 Minutes",
    u"360° Géo",
    u"ARTE Journal",
    u"ARTE Junior",
    u"Court-circuit",
    u"Cuisines des terroirs",
    u"Karambolage",
    u"Maestro",
    u"Personne ne bouge !",
    u"Square",
    u"Vox Pop",
    u"Xenius",
    u"Yourope"
]
currently abandonned.

"""
ArteUrls = [
    "http://www.arte.tv/guide/fr/plus7/cinema?date=j-0",
    "http://www.arte.tv/guide/fr/plus7/actu-societe?date=j-0",
    "http://www.arte.tv/guide/fr/plus7/arts-spectacles-classiques?date=j-0",
    "http://www.arte.tv/guide/fr/plus7/culture-pop?date=j-0",
    "http://www.arte.tv/guide/fr/plus7/decouverte?date=j-0",
    "http://www.arte.tv/guide/fr/plus7/histoire?date=j-0"
]

ArteCats = [
    u"Cinéma",
    u"Actu & Société",
    u"Arts & Spectacles",
    u"Culture Pop",
    u"Découvertes",
    u"Histoire"
]


def checkIfExcluded(t):
    for excluded in excludedVideos:
        if excluded.lower() in t.lower():
            return True
    return False


def getVideosList(url, catName):
    pat = re.compile('data-categoryVideoSet="(.+?)"')
    sock = urllib.urlopen(url)
    videosJson = pat.findall(sock.read())
    if len(videosJson) == 0:
        return
    videosJson = videosJson[0]
    sock.close()

    videosJson = videosJson.replace("&quot;", '"').replace("\/", "/")
    vids = json.loads(videosJson)["videos"]

    for v in vids:
        #if checkIfExcluded(v["title"]):
        #    continue

        element = {}
        element["title"] = BeautifulSoup(v["title"], "html.parser").text
        element["link"] = v["url"]
        element["description"] = v["teaser"]
        element["duration"] = int(ceil(v["duration"] / 60))
        element["date"] = mktime(datetime.strptime(v["scheduled_on"],
                                                   "%Y-%m-%d").timetuple())
        element["category"] = catName
        element["views"] = v["views"]
        element["rights_end"] = mktime(datetime.strptime(v["rights_end"],
                                                         "%Y-%m-%dT%H:%M:%SZ").timetuple())
        data[v["url"]] = element

if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')



    gc = pygsheets.authorize(
        service_file='##############################################')
    sh = gc.open_by_key('##############################################')
    wks = sh.worksheet('title','ArtePlus7')

    for (url, cat) in zip(ArteUrls, ArteCats):
        print(url)
        getVideosList(url, cat)
        sleep(1)

    with open('db-arte.json') as json_data:
        oldData = json.load(json_data)

    for key in data.keys():
        if not key in oldData:  # new data
            row = []
            row.append(
                '=HYPERLINK( "' + data[key]['link'] + '" ; "' + data[key]['title'].replace('"', '\"') + '" )')
            if data[key]['description'] != None:
                row.append(BeautifulSoup(data[key]['description'], "html.parser").text)
            else:
                row.append("")
            row.append(str(data[key]['duration']) + 'mn')
            row.append(datetime.fromtimestamp(
                data[key]['date']).strftime('%A %d %B'))
            row.append(data[key]['category'])
            row.append(datetime.fromtimestamp(
                data[key]['rights_end']).strftime('%A %d %B'))
            row.append('')

            wks.insert_rows(row=3, values=row)
            oldData[key] = data[key]
            sleep(2)

    with open('db-arte.json', 'w') as outfile:
        json.dump(oldData, outfile)
