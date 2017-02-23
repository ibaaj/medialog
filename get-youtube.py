# -*- coding: utf-8 -*-
import locale
import json
import requests
import time
from datetime import datetime, timedelta
import pygsheets
from time import mktime,sleep
from bs4 import BeautifulSoup

data = {}

baseURL = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId='
endURL = '&key=##############################################'

playlists = [
"PL61mLQTC4oQe_CRDif81yc12uOhsge4Zq", # axolot
"PLl5zW0Z-tqm6SL5omJXkMxXwS8aJEZA65", # dirty biology
"PLpsyM5kZ1kcyTc1vct8i5u1psfKeVAQL8", # doc seven geo
"PLpsyM5kZ1kczupqozGGDhcIRJ0ymQii9M", # doc seven nature
"PLpsyM5kZ1kcxctp3swEWs1_DmM2uTzHX3", # doc seven 7min
"PLpsyM5kZ1kczb_knD4MlmLFa4_Y9nzLI9", # doc seven sci & tech
"PLpsyM5kZ1kcxLC6dYD7L7Y85EY6Ur6r1k", # doc seven lieux insolites
"PLpsyM5kZ1kcx6iEXhwecVkcFh9KDXdJqY", # doc seven vie quotidienne
"PLpsyM5kZ1kczycPMyajpR5_QkFGRAzt-A", # doc seven histoire
"PLpsyM5kZ1kcw0ANulnQtp8bDnSF1xSnRr", # doc seven voyage/geo
"PLpsyM5kZ1kcxYoaP_72UXuWik5WvFHaXs", # doc seven art & culture
"PLpsyM5kZ1kcwzkWgmO7GUBiFejWFd5VLs", # doc seven faits div
"PLpsyM5kZ1kcyVDnPS_QmNPTyyECoKGAVp", # doc seven sport
"PL2hPqlLCZubNAWBZkCWLf0YUeb9WxiF6C",  # revue du monde
"PL2hPqlLCZubNMR6VOtPGfIhgDmFbprfjn", # th du monde
"PLGPWPtcc-r803DEOS637KaAju2722lqwW", # e-penser humain/vie
"PLGPWPtcc-r83QfCPHiCbHk31HJeeZBtHj", # e-penser univers
"PLGPWPtcc-r820-4zUGi_7nDw5Lk98mTbi", # e-penser electromagnetisme, lux
"PLFNT0EUxKoycE2hAbLJi9oI7-scQ7oOny", # plph histoire du monde
"PLFNT0EUxKoyf9KZjNESBgBv8wnaXe_vRN", # plph de a à z
]

authors = [
    "Axolot",
    "Dirty Biology",
    "Doc Seven",
    "Doc Seven",
    "Doc Seven",
    "Doc Seven",
    "Doc Seven",
    "Doc Seven",
    "Doc Seven",
    "Doc Seven",
    "Doc Seven",
    "Doc Seven",
    "Doc Seven",
    "Revue du Monde",
    "Théorie du Monde",
    "e-penser",
    "e-penser",
    "e-penser",
    "Pour la petite Histoire",
    "Pour la petite Histoire"
]

def getYoutubeVideoList(urlYoutube, YTauthor):
    print(urlYoutube)
    resp = requests.get(url=urlYoutube)
    respdata = json.loads(resp.text)
    now = datetime.now()


    for d in respdata["items"]:
        v = datetime.strptime(d["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
        if now - timedelta(hours=24) <= v <= now:
            description = d["snippet"]["description"]
            description = description.replace('\n','').replace('\r','')
            description = (description[:140] + '...') if len(description) > 140 else description
            element = {}
            element["title"] = d["snippet"]["title"]
            element["description"] = description
            element["link"] = "https://youtube.com/watch?v=" + d["snippet"]["resourceId"]["videoId"]
            element["duration"] = ""  # in this json there is no duration element
            element["date"] = mktime(datetime.strptime(d["snippet"]["publishedAt"],
                                                             "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())
            element["author"] = YTauthor
            data["https://youtube.com/watch?v=" + d["snippet"]
                 ["resourceId"]["videoId"]] = element


if __name__ == "__main__":
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

        gc = pygsheets.authorize(
            service_file='##############################################.json')
        sh = gc.open_by_key('##############################################')

        wks = sh.worksheet('title','Youtube')

        for pl,author in zip(playlists,authors):
            getYoutubeVideoList(baseURL + pl + endURL,author)

        with open('db-youtube.json') as json_data:
            oldData = json.load(json_data)

        for key in data.keys():
            if not key in oldData:  # new data
                row = []
                row.append(
                    '=HYPERLINK( "' + data[key]['link'] + '" ; "' + data[key]['title'].replace('"', '\"') + '" )')
                row.append(BeautifulSoup(
                    data[key]['description'], "html.parser").text)

                row.append(datetime.fromtimestamp(
                    data[key]['date']).strftime('%A %d %B %Y'))
                row.append(data[key]['author'])

                wks.insert_rows(row=3, values=row)
                oldData[key] = data[key]
            sleep(2)

        with open('db-youtube.json', 'w') as outfile:
            json.dump(oldData, outfile)
