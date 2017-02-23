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


urlAllocine = 'http://rss.allocine.fr/ac/cine/cettesemaine?format=xml'

data = {}


def getAllocineShowsList():
    d = feedparser.parse(urlAllocine)

    cleanr = re.compile('<.*?>')

    for entry in d['entries']:
        element = {}

        cleandescription = re.sub(cleanr, '', entry['description'])

        #print(cleandescription)
        description = ""
        descriptionParts = []
        who = []
        real = ""
        actors = ""
        duration = ""
        genre = ""

        try:
            description = cleandescription.split(') - ')[1]
            descriptionParts = cleandescription.split('Un film de ')
            if len(descriptionParts) > 1:
                who = (descriptionParts[1].split('>> Fiche compl')[0].split(
                'Spectateurs')[0].split('Presse :')[0]).split('Avec ')
                real = who[0]
                if len(who) > 1:
                    actors = who[1]

            duration = descriptionParts[0].split(') - ')[0].split(' (')[1]
            genre = descriptionParts[0].split(' (')[0]
        except:
            pass

        element['title'] = entry['title']
        element['link'] = entry['link']
        element['description'] = description
        element['duration'] = duration
        element['actors'] = actors
        element['real'] = real
        element['genre'] = genre

        data[element['link']] = element


if __name__ == "__main__":
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

        gc = pygsheets.authorize(
            service_file='##############################################.json')
        sh = gc.open_by_key('##############################################')

        wks = sh.worksheet('title','Cinema')

        getAllocineShowsList()

        with open('db-allocine.json') as json_data:
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
                row.append(data[key]['genre'])
                row.append(data[key]['duration'])
                row.append(data[key]['real'])
                row.append(data[key]['actors'])

                wks.insert_rows(row=3, values=row)
                oldData[key] = data[key]
                sleep(2)

        with open('db-allocine.json', 'w') as outfile:
            json.dump(oldData, outfile)
