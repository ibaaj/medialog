# -*- coding: utf-8 -*-
import feedparser
import locale
import json
import requests
import time
from datetime import datetime, timedelta
import pygsheets
from time import mktime,sleep
from bs4 import BeautifulSoup
import re
import urllib

urlNetflix = 'http://dvd.netflix.com/NewReleasesRSS'

data = {}

def getNetflixShowsList():
    d = feedparser.parse(urlNetflix)
    cleanr = re.compile('<.*?>')


    for entry in d['entries']:
        cleandescription = re.sub(cleanr, '', entry['description'])
        element = {}
        element['title'] = entry['title']
        element['link'] = entry['link']
        element['description'] = cleandescription
        element['allocine'] = 'http://www.allocine.fr/recherche/?q=' + \
            urllib.quote(entry['title'])
        data[element['link']] = element


if __name__ == "__main__":
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

        gc = pygsheets.authorize(
            service_file='##############################################')
        sh = gc.open_by_key('##############################################')

        wks = sh.worksheet('title','Netflix')

        getNetflixShowsList()

        with open('db-netflix.json') as json_data:
            oldData = json.load(json_data)

        start = datetime.now() - timedelta(days=datetime.now().weekday())

        for key in data.keys():
            if not key in oldData:  # new data
                row = []
                row.append(
                    '=HYPERLINK( "' + data[key]['link'] + '" ; "' + data[key]['title'].replace('"', '\"') + '" )')
                row.append(BeautifulSoup(
                    data[key]['description'], "html.parser").text)

                row.append(start.strftime('%A %d %B'))
                row.append(data[key]['allocine'])

                wks.insert_rows(row=3, values=row)
                oldData[key] = data[key]
            time.sleep(2)

        with open('db-netflix.json', 'w') as outfile:
            json.dump(oldData, outfile)
