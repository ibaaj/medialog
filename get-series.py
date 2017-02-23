from datetime import date,datetime,timedelta
from time import mktime
import urllib2
import urllib
from bs4 import BeautifulSoup
import calendar
import locale
import pygsheets
import calendar
from time import sleep
from itertools import izip
from collections import OrderedDict
import sys

data = OrderedDict()
datelist = []

def increment_month(when):
    days = calendar.monthrange(when.year, when.month)[1]
    return when + timedelta(days=days)

def get_datetime_range(year, month):
    nb_days = calendar.monthrange(year, month)[1]
    return [date(year, month, day) for day in range(1, nb_days+1) if date(year, month, day) >= datetime.now().date()]

def parse():
    today = datetime.now().strftime("%Y-%m-%d").split('-')
    dateList = get_datetime_range(int(today[0]),int(today[1]))
    #print(d)
    p = 'http://www.pogdesign.co.uk/cat/'
    page = urllib2.urlopen(p).read()
    soup = BeautifulSoup(page, 'html.parser')
    soup.prettify()
    for d in dateList:
        print(('d_' + d.strftime("%d_%m_%Y")).replace("_0", "_"))
        eventsHTML = soup.findAll('div', {'id': 'd_' + d.strftime("%d_%m_%Y").replace("_0", "_")})
        eventsHTML = eventsHTML[0]

        eventsList = eventsHTML.findAll('div', {'class': 'ep'})
        for e in eventsList:
            l = [x for x in e.text.split('\n') if x]
            l.append('1' if 'pep' in e['class'] else '0') # n
            l.append('1' if 'lep' in e['class'] else '0') # f
            l.append('1' if 'fep' in e['class'] else '0') # ns

            if d.strftime("%d-%m-%Y") not in data:
                data[d.strftime("%d-%m-%Y")] = []
            data[d.strftime("%d-%m-%Y")].append(l)
    sleep(2)

    dateLooped = increment_month(datetime.now())

    for i in range(0,11):
        pdate = dateLooped.strftime("%Y-%m-%d").split('-')
        dateList = get_datetime_range(int(pdate[0]),int(pdate[1]))

        p = 'http://www.pogdesign.co.uk/cat/' + pdate[1].lstrip("0") + '-' + pdate[0]
        page = urllib2.urlopen(p).read()
        soup = BeautifulSoup(page, 'html.parser')
        soup.prettify()
        for d in dateList:
            print(('d_' + d.strftime("%d_%m_%Y")).replace("_0", "_"))
            eventsHTML = soup.findAll('div', {'id': ('d_' + d.strftime("%d_%m_%Y")).replace("_0", "_")})
            eventsHTML = eventsHTML[0]

            eventsList = eventsHTML.findAll('div', {'class': 'ep'})
            for e in eventsList:
                l = [x for x in e.text.split('\n') if x]
                l.append('1' if 'pep' in e['class'] else '0') # n
                l.append('1' if 'lep' in e['class'] else '0') # ns
                l.append('1' if 'fep' in e['class'] else '0') # f

                if d.strftime("%d-%m-%Y") not in data:
                    data[d.strftime("%d-%m-%Y")] = []
                data[d.strftime("%d-%m-%Y")].append(l)

        dateLooped = increment_month(dateLooped)
        sleep(2)


if __name__ == "__main__":
    parse()
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    gc = pygsheets.authorize(
        service_file='##############################################')
    sh = gc.open_by_key('##############################################')

    wks = sh.worksheet('title','Series')


    k = 4

    for d in data:
        for h in data[str(d)]:
            imdb = "http://www.imdb.com/find?s=all&q=" + urllib.quote(h[0])
            allocine = 'http://www.allocine.fr/recherche/?q=' + urllib.quote(h[0])
            row = []
            row.append(d)
            row.append(h[0])
            row.append(h[1])
            row.append(h[2])
            row.append(h[3])
            row.append(h[4])
            row.append('=HYPERLINK( "' + imdb + '" ; "' + imdb + '" )')
            row.append('=HYPERLINK( "' + allocine + '" ; "' + allocine + '" )')

            wks.insert_rows(row=k, values=row)
            k=k+1
            sleep(2)
    wks.delete_rows(k,number=2000)
