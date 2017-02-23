from datetime import date,datetime,timedelta
from time import mktime
import urllib2
from bs4 import BeautifulSoup
import calendar
import locale
import pygsheets
from time import sleep

data = {}
datelist = []

def parseMonth(dt):
    today = dt.strftime("%Y-%m-%d").split('-')
    d = str(int(today[2]))
    m = str(int(today[1]))
    y = today[0]
    p = 'https://www.residentadvisor.net/events.aspx?ai=44&v=month&mn=' + m + '&yr='+ y + '&dy=' + d

    page = urllib2.urlopen(p).read()
    soup = BeautifulSoup(page, 'html.parser')
    soup.prettify()
    ulEvents = soup.findAll('ul', {'id': 'items'})[0]
    eventsHTML = ulEvents.findAll('article', {'class': 'event-item'})

    for s in eventsHTML:
        d = s.findAll('time')[0].text
        a = s.findAll('h1')[0].findAll('a')[0]
        href = a['href']
        event = a.text
        location = a.find_next_sibling('span').text.split('at ')[1]
        time =  mktime(datetime.strptime(d, "%Y-%m-%dT%H:%M").timetuple())
        if str(int(time)) not in data:
            data[str(int(time))] = {}
            datelist.append(int(time))
        data[str(int(time))][href] = [event,href,location,time]

if __name__ == "__main__":
    def increment_month(when):
        days = calendar.monthrange(when.year, when.month)[1]
        return when + timedelta(days=days)

    now = datetime.now()
    parseMonth(now)

    for i in (range(0,3)):
        now = increment_month(now)
        parseMonth(now)

    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    gc = pygsheets.authorize(
        service_file='##############################################')
    sh = gc.open_by_key('##############################################')

    wks = sh.worksheet('title','EventsInParis')


    k = 3
    for d in datelist:
        for h in data[str(d)]:
            row = []
            row.append(datetime.fromtimestamp(data[str(d)][h][3]).strftime('%A %d %B'))
            row.append(
                '=HYPERLINK( "https://www.residentadvisor.net' + data[str(d)][h][1] + '" ; "' + data[str(d)][h][0].replace('"', '\"') + '" )')
            row.append(data[str(d)][h][2])

            wks.insert_rows(row=k, values=row)
            k=k+1
            sleep(2)
    wks.delete_rows(k,number=200)
