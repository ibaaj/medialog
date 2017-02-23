# -*- coding: utf-8 -*-
import feedparser
import locale
import json
import requests
import time
from datetime import datetime, timedelta
import pygsheets
from time import mktime
from bs4 import BeautifulSoup
import re
import urllib


data = {}

def getReviewShowsList(url, reviewType):
    d = feedparser.parse(url)
    cleanr = re.compile('<.*?>')

    for entry in d['entries']:
        cleandescription = re.sub(cleanr, '', entry['description'])
        element = {}
        element['title'] = BeautifulSoup(entry['title'], 'html.parser').text
        element['link'] = entry['link']
        element['description'] = cleandescription

        if entry.published_parsed is None:
            entry.published_parsed = datetime.strptime(entry.published,
                                                             "%a, %d %b %Y %H:%M").timetuple()
        element['date'] = mktime(entry.published_parsed)
        element["type"] = reviewType[:-2]
        element["best"] = "1" if reviewType == "Pitchfork Albums B" or reviewType == "Pitchfork Tracks B" else "0"
        data[element['link']] = element



if __name__ == "__main__":


        gc = pygsheets.authorize(
            service_file='#######################################.json')
        sh = gc.open_by_key('##################################################')

        wks = sh.worksheet('title','MusicReview')

        getReviewShowsList('http://pitchfork.com/rss/reviews/albums/', 'Pitchfork Album  ')
        getReviewShowsList('http://pitchfork.com/rss/reviews/tracks/', 'Pitchfork Tracks  ')

        getReviewShowsList('http://pitchfork.com/rss/reviews/best/albums/', "Pitchfork Albums B")
        getReviewShowsList('http://pitchfork.com/rss/reviews/best/tracks/', "Pitchfork Tracks B")

        getReviewShowsList('https://www.residentadvisor.net/xml/reviews.xml', 'RA  ')
        getReviewShowsList('http://www.seeksicksound.com/feed/', 'SeekSickSound  ')


        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        with open('db-review.json') as json_data:
            oldData = json.load(json_data)


        for key in data.keys():
            if not key in oldData:  # new data
                row = []
                row.append(
                    '=HYPERLINK( "' + data[key]['link'] + '" ; "' + data[key]['title'].replace('"', '') + '" )')
                row.append(BeautifulSoup(
                    data[key]['description'], "html.parser").text)

                row.append(datetime.fromtimestamp(int(data[key]['date'])).strftime('%Y-%m-%d'))
                row.append(data[key]['type'])
                row.append(data[key]['best'])

                wks.insert_rows(row=3, values=row)
                time.sleep(2)

                oldData[key] = data[key]

        with open('db-review.json', 'w') as outfile:
            json.dump(oldData, outfile)
